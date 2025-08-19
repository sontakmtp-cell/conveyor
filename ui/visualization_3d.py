# ui/visualization_3d.py
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import math
import os
import sys
import tempfile

from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QCheckBox,
    QComboBox,
    QSlider,
    QVBoxLayout,
    QWidget,
)


def get_resource_path(relative_path: str) -> str:
    """Return absolute resource path for both dev and PyInstaller bundle."""
    # Revised: Use getattr to detect PyInstaller _MEIPASS and keep full relative path
    base_path = getattr(sys, "_MEIPASS", None)
    if base_path:
        return os.path.join(base_path, relative_path)
    # If not bundled, compute path relative to project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    return os.path.join(project_root, relative_path)


class Visualization3DWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.current_params = None
        self.current_result = None
        self.theme = "light"
        self._is_fullscreen = False
        self._saved_geometry = None
        self._saved_window_state = None
        self._temp_html_file: tempfile.NamedTemporaryFile | None = None

        self._build_ui()
        self._wire()
        self._load_scene()

    # ---------------- UI ----------------
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        grp = QGroupBox("Tùy chọn hiển thị 3D")
        gl = QHBoxLayout(grp)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("Góc nhìn:"))
        self.view_combo = QComboBox()
        self.view_combo.addItems(["Isometric", "Top View", "Side View", "Front View"])
        vbox.addWidget(self.view_combo)
        gl.addLayout(vbox)

        tbox = QVBoxLayout()
        self.chk_anim = QCheckBox("Animation chuyển động")
        self.chk_anim.setChecked(True)
        self.chk_material = QCheckBox("Hiển thị dòng vật liệu")
        self.chk_material.setChecked(True)
        self.chk_forces = QCheckBox("Vector lực căng")
        self.chk_heat = QCheckBox("Heat map stress")
        tbox.addWidget(self.chk_anim)
        tbox.addWidget(self.chk_material)
        tbox.addWidget(self.chk_forces)
        tbox.addWidget(self.chk_heat)
        gl.addLayout(tbox)

        sbox = QVBoxLayout()
        sbox.addWidget(QLabel("Tốc độ animation:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(50)
        sbox.addWidget(self.speed_slider)
        gl.addLayout(sbox)

        abox = QHBoxLayout()
        self.btn_reset = QPushButton("Reset Camera")
        self.btn_full = QPushButton("Toàn màn hình 3D")
        self.btn_shot = QPushButton("Chụp ảnh 3D")
        abox.addWidget(self.btn_reset)
        abox.addWidget(self.btn_full)
        abox.addWidget(self.btn_shot)
        gl.addLayout(abox)

        layout.addWidget(grp)

        self.web = QWebEngineView(self)
        self.web.setContextMenuPolicy(Qt.NoContextMenu)
        layout.addWidget(self.web, 1)

    def _wire(self) -> None:
        self.chk_anim.toggled.connect(self._toggle_anim)
        self.chk_material.toggled.connect(self._toggle_material)
        self.chk_forces.toggled.connect(self._toggle_forces)
        self.chk_heat.toggled.connect(self._toggle_heat)

        self.view_combo.currentTextChanged.connect(self._change_view)
        self.speed_slider.valueChanged.connect(self._change_speed)

        self.btn_reset.clicked.connect(self._reset_cam)
        self.btn_full.clicked.connect(self._toggle_fullscreen)
        self.btn_shot.clicked.connect(self._screenshot)

    # -------------- Data helpers --------------
    @staticmethod
    def _safe(obj, name: str, default):
        try:
            v = getattr(obj, name, default)
        except Exception:
            v = default
        return v if v is not None else default

    def _derive(self) -> dict:
        p = self.current_params
        r = self.current_result

        L = float(self._safe(p, "L_m", 10.0))
        W = float(self._safe(p, "B_mm", 800.0)) / 1000.0
        H = float(self._safe(p, "H_m", 2.0))
        V = float(self._safe(p, "V_mps", 2.5))
        alpha_deg = self._safe(p, "inclination_deg", None)
        alpha = math.radians(alpha_deg) if isinstance(alpha_deg, (int, float)) else (
            math.atan2(H, L) if L > 0 else 0.0
        )

        trough_label = str(self._safe(p, "trough_angle_label", "20°"))
        idler_spacing = float(self._safe(p, "carrying_idler_spacing_m", 1.2))
        power = float(self._safe(r, "motor_power_kw", 50.0))

        distances = list(self._safe(r, "distances_m", []) or [])
        t_profile = list(self._safe(r, "tension_profile", []) or [])
        if distances and len(t_profile) != len(distances):
            t_profile = [0.0] * len(distances)

        try:
            import re

            m = re.search(r"(\d+)", trough_label)
            trough_deg = float(m.group(1)) if m else 20.0
        except Exception:
            trough_deg = 20.0

        width_mm = W * 1000.0
        if width_mm < 800:
            pulley_d = 0.30
        elif width_mm < 1000:
            pulley_d = 0.35
        elif width_mm < 1200:
            pulley_d = 0.40
        elif width_mm < 1400:
            pulley_d = 0.50
        elif width_mm < 1600:
            pulley_d = 0.56
        else:
            pulley_d = 0.63

        glb_local = get_resource_path("ui/models/Bang_tai_4m.glb")
        model_url = ""
        if os.path.exists(glb_local):
            model_url = QUrl.fromLocalFile(glb_local).toString()

        return {
            "length": max(4.0, L),
            "width": max(0.3, W),
            "height": max(0.0, H),
            "alpha": float(alpha),
            "speed": max(0.05, V),
            "power": power,
            "trough_deg": trough_deg,
            "idler_spacing": max(0.6, idler_spacing),
            "pulley_d": pulley_d,
            "distances": distances,
            "tension": t_profile,
            "modelUrl": model_url,
        }

    # -------------- JS libs (LOCAL FIRST) --------------
    def _read_local_js(self, rel_path: str) -> str | None:
        try:
            full = get_resource_path(rel_path)
            if os.path.exists(full) and os.path.getsize(full) > 10_000:
                with open(full, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
        except Exception:
            pass
        return None

    def _three_and_loader_tags(self) -> str:
        """
        Assemble script tags to load Three.js and GLTFLoader as ES modules.
        For the purposes of this application, we always load the module versions
        from a CDN. This avoids the "Cannot use import statement outside a module"
        error observed when using non‑module UMD builds. A minimal inline
        fallback for GLTF parsing is retained in case GLTFLoader is unavailable.
        """
        parts: list[str] = []

        # If a local UMD build of Three.js is available, include it first as a normal
        # script. This defines `THREE` on the global object and ensures our
        # lightweight fallback GLTF parser can work even when the module build
        # fails to load (for example, when running offline). The UMD build is
        # loaded using a non‑module script tag.
        three_local_path = get_resource_path("ui/js/three.min.js")
        if os.path.exists(three_local_path):
            parts.append(f'<script src="{QUrl.fromLocalFile(three_local_path).toString()}"></script>')

        # Always load the module version of three.js. Using the UMD build in a
        # module context will not work because it doesn’t expose named exports.
        parts.append(
            '<script type="module" src="https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.module.js"></script>'
        )

        # Load the module version of GLTFLoader from the examples/jsm path. This
        # loader uses ES module syntax and expects the `three` module to be
        # available. Loading it with type="module" satisfies that requirement.
        parts.append(
            '<script type="module" src="https://cdn.jsdelivr.net/npm/three@0.157.0/examples/jsm/loaders/GLTFLoader.js"></script>'
        )

        # Minimal inline fallback in case THREE.GLTFLoader is missing. The code
        # implements a very simple GLB parser and defines a LiteLoader on the
        # global THREE namespace so that the application can still display
        # reference models when packaged offline. It is defined in a normal
        # script tag (non‑module) because it operates on the global THREE.
        parts.append(
            """
    <script>
    (function(){
      if (typeof THREE==='undefined' || typeof THREE.GLTFLoader!=='undefined') return;
      function readU32(dv,o){return dv.getUint32(o,true);}
      function tdec(){return (typeof TextDecoder!=='undefined')?new TextDecoder('utf-8'):{decode:(a)=>{let s='';for(let i=0;i<a.length;i++)s+=String.fromCharCode(a[i]);try{return decodeURIComponent(escape(s))}catch(e){return s}}};}
      function accSize(t){return t==='SCALAR'?1:t==='VEC2'?2:t==='VEC3'?3:t==='VEC4'?4:t==='MAT2'?4:t==='MAT3'?9:t==='MAT4'?16:3;}
      function compArr(ct){switch(ct){case 5120:return Int8Array;case 5121:return Uint8Array;case 5122:return Int16Array;case 5123:return Uint16Array;case 5125:return Uint32Array;case 5126:return Float32Array;default:return Float32Array;}}
      function parseGLB(ab,onLoad,onError){
        try{
          const dv=new DataView(ab); if(readU32(dv,0)!==0x46546C67) throw new Error('Not GLB');
          const len=readU32(dv,8); let off=12, json=null, bin=null;
          while(off<len){const clen=readU32(dv,off);off+=4;const ctyp=readU32(dv,off);off+=4;const sub=new Uint8Array(ab,off,clen);off+=clen;
            if(ctyp===0x4E4F534A) json=JSON.parse(tdec().decode(sub)); else if(ctyp===0x004E4942) bin=ab.slice(off-clen,off);}
          if(!json) throw new Error('JSON missing');
          const nodes=json.nodes||[], meshes=json.meshes||[], accs=json.accessors||[], views=json.bufferViews||[], mats=json.materials||[];
          function getAcc(i){const a=accs[i],bv=views[a.bufferView]||{},bo=(bv.byteOffset||0)+(a.byteOffset||0);const C=compArr(a.componentType),sz=accSize(a.type),cnt=a.count;return{arr:new C(bin||ab,bo,sz*cnt),itemSize:sz};}
          function makeAttr(g,n,a){g.setAttribute(n,new THREE.BufferAttribute(a.arr,a.itemSize));}
          function mOf(md){const p=md&&md.pbrMetallicRoughness||{},b=p.baseColorFactor||[0.8,0.8,0.8,1];const m=p.metallicFactor??0.2,r=p.roughnessFactor??0.7;return new THREE.MeshStandardMaterial({color:new THREE.Color(b[0],b[1],b[2]),metalness:m,roughness:r});}
          function buildMesh(idx){const m=meshes[idx]; if(!m||!m.primitives||!m.primitives.length) return new THREE.Object3D(); const p=m.primitives[0]; const g=new THREE.BufferGeometry();
            if(p.attributes.POSITION!=null){const a=getAcc(p.attributes.POSITION);makeAttr(g,'position',a);g.computeBoundingSphere();g.computeBoundingBox();}
            if(p.attributes.NORMAL!=null){makeAttr(g,'normal',getAcc(p.attributes.NORMAL));}
            if(p.attributes.TEXCOORD_0!=null){makeAttr(g,'uv',getAcc(p.attributes.TEXCOORD_0));}
            if(p.indices!=null){const ai=getAcc(p.indices);g.setIndex(new THREE.BufferAttribute(ai.arr,1));}
            const mesh=new THREE.Mesh(g,mOf(mats[p.material])); mesh.castShadow=mesh.receiveShadow=true; return mesh;}
          const objs=[]; for(let i=0;i<nodes.length;i++){const n=nodes[i]; const o=(n.mesh!=null?buildMesh(n.mesh):new THREE.Object3D()); const t=n.translation||[0,0,0], r=n.rotation||[0,0,0,1], s=n.scale||[1,1,1];
            o.position.set(t[0],t[1],t[2]); o.quaternion.set(r[0],r[1],r[2],r[3]); o.scale.set(s[0],s[1],s[2]); objs[i]=o;}
          for(let j=0;j<nodes.length;j++){const n=nodes[j]; if(n.children){for(let c=0;c<n.children.length;c++){const ci=n.children[c]; if(objs[ci]) objs[j].add(objs[ci]);}}}
          const sidx=(json.scene!=null)?json.scene:0, sc=(json.scenes&&json.scenes[sidx])||{nodes:[]}, root=new THREE.Group(); for(const ni of sc.nodes){if(objs[ni]) root.add(objs[ni]);}
          onLoad && onLoad({scene:root, scenes:[root]});
        }catch(e){onError&&onError(e);}
      }
      function LiteLoader(){this.manager=THREE.DefaultLoadingManager;}
      LiteLoader.prototype.load=function(url,onLoad,onProgress,onError){
        const x=new XMLHttpRequest(); x.open('GET',url,true); x.responseType='arraybuffer';
        if(onProgress) x.onprogress=onProgress; x.onerror=()=>onError&&onError(new Error('Network error'));
        x.onload=()=>{ if(x.status>=200&&x.status<300) parseGLB(x.response,onLoad,onError); else onError&&onError(new Error('HTTP '+x.status)); };
        try{x.send(null);}catch(e){onError&&onError(e);}
      };
      THREE.GLTFLoader = LiteLoader;
    })();
    </script>
            """.strip()
        )

        return "\n".join(parts)

    # -------------- HTML/JS --------------
    def _generate_html(self) -> str:
        d = self._derive()
        libs = self._three_and_loader_tags()
        bg = "#0f172a" if self.theme == "dark" else "#f8fafc"
        fg = "#e2e8f0" if self.theme == "dark" else "#0f172a"
        alpha_deg = d["alpha"] * 180.0 / math.pi

        return f"""<!DOCTYPE html>
    <html lang="vi"><head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>3D Conveyor</title>
    <style>
     html,body {{height:100%;margin:0;overflow:hidden;background:{bg};}}
     #hud {{
       position:fixed; left:12px; top:12px; padding:8px 10px; background:rgba(0,0,0,.35);
       color:{fg}; font:12px/1.4 system-ui; border-radius:8px; z-index:10; pointer-events:none;
     }}
    </style>
    </head>
    <body>
    <div id="hud">L={d["length"]:.1f} m • W={d["width"]:.2f} m • H={d["height"]:.1f} m • α={alpha_deg:.1f}° • v={d["speed"]:.2f} m/s</div>
    {libs}
    <script>
    let scene,camera,renderer;
    let rootGroup, rollers=[], headPulley, tailPulley, materialPts, forceArrows, refModel;
    let anim=true, conveyorSpeed={d["speed"]:.3f};
    const data={json.dumps(d)};

    // Orbit-lite globals
    let orbitTarget = new THREE.Vector3(0, data.height/2, 0);
    let orbitRadius = 10, orbitTheta = 0.9, orbitPhi = 1.0;

    function assertThree(){{
      if(typeof THREE==='undefined'){{
        const d=document.createElement('div');
        d.style.cssText='position:fixed;inset:0;display:flex;align-items:center;justify-content:center;color:#fff;background:#ef4444';
        d.innerHTML='Không tải được three.js. Kiểm tra ui/js/three.min.js';
        document.body.appendChild(d);
        return false;
      }}
      return true;
    }}

    function fitCameraToObject(obj, margin=1.3){{
      if(!obj) return;
      const box = new THREE.Box3().setFromObject(obj);
      if(!box.isEmpty()){{
        const size = box.getSize(new THREE.Vector3());
        const center = box.getCenter(new THREE.Vector3());

        // Set new orbit target to object center
        orbitTarget.copy(center);

        // Compute distance from FOV & aspect
        const maxSize = Math.max(size.x, size.y, size.z);
        const fov = camera.fov * (Math.PI/180);
        const aspect = renderer.domElement.clientWidth / renderer.domElement.clientHeight;
        const fitHeightDistance = (size.y/2) / Math.tan(fov/2);
        const fitWidthDistance  = (size.x/2) / (Math.tan(fov/2) * aspect);
        let distance = Math.max(fitHeightDistance, fitWidthDistance, maxSize) * margin;

        // Move camera along current direction to the new distance
        const dir = new THREE.Vector3()
          .subVectors(camera.position, center)
          .normalize();
        if(!isFinite(dir.length()) || dir.length()===0){{
          dir.set(1,0.5,1).normalize();
        }}
        camera.position.copy(center).addScaledVector(dir, distance);

        // Update near/far generously
        camera.near = Math.max(0.01, distance/100);
        camera.far  = Math.max(5000, distance*100);
        camera.updateProjectionMatrix();

        // Update orbit params
        orbitRadius = distance;
        const dx = camera.position.x - orbitTarget.x;
        const dy = camera.position.y - orbitTarget.y;
        const dz = camera.position.z - orbitTarget.z;
        orbitTheta = Math.atan2(dz, dx);
        const r = Math.sqrt(dx*dx + dy*dy + dz*dz);
        orbitPhi = Math.acos(THREE.MathUtils.clamp(dy/r, -1, 1));

        updateCameraFromOrbit();
      }}
    }}

    function updateCameraFromOrbit(){{
      // Clamp phi to avoid gimbal lock
      const EPS = 0.001;
      orbitPhi = Math.max(EPS, Math.min(Math.PI - 0.4, orbitPhi));
      // Clamp radius
      orbitRadius = THREE.MathUtils.clamp(orbitRadius, 0.1, 1e6);

      camera.position.set(
        orbitTarget.x + orbitRadius * Math.sin(orbitPhi) * Math.cos(orbitTheta),
        orbitTarget.y + orbitRadius * Math.cos(orbitPhi),
        orbitTarget.z + orbitRadius * Math.sin(orbitPhi) * Math.sin(orbitTheta)
      );
      camera.lookAt(orbitTarget);
    }}

    function makeRoller(radius, length, pos, tiltRad){{
      const geo = new THREE.CylinderGeometry(radius, radius, length, 28);
      const mat = new THREE.MeshStandardMaterial({{color:0x6b7280, metalness:.15, roughness:.8}});
      const cyl = new THREE.Mesh(geo, mat);
      cyl.userData.radius = radius;
      const pivot = new THREE.Group();
      pivot.add(cyl);
      pivot.position.copy(pos);
      if(tiltRad !== 0){{
        const sign = (pos.z >= 0 ? 1 : -1);
        pivot.rotation.x = -sign * Math.abs(tiltRad);
      }}
      rootGroup.add(pivot);
      return cyl;
    }}

    function makePulley(radius, length, pos){{
      const geo = new THREE.CylinderGeometry(radius, radius, length, 64);
      const mat = new THREE.MeshStandardMaterial({{color:0x374151, metalness:.3, roughness:.6}});
      const m = new THREE.Mesh(geo, mat);
      m.rotation.x = Math.PI/2;
      m.position.copy(pos);
      rootGroup.add(m);
      return m;
    }}

    function buildMaterial(){{
      const count=300;
      const g=new THREE.BufferGeometry();
      const arr=new Float32Array(count*3);
      for(let i=0; i<count; i++){{
        arr[i*3] = (Math.random()-0.5)*data.length*0.9;
        arr[i*3+1] = data.height/2 + 0.06;
        arr[i*3+2] = (Math.random()-0.5)*data.width*0.8;
      }}
      g.setAttribute('position', new THREE.BufferAttribute(arr, 3));
      const m=new THREE.PointsMaterial({{size:0.05}});
      return new THREE.Points(g, m);
    }}

    function buildForcesFromProfile(){{
      const grp=new THREE.Group();
      const xs = data.distances || [];
      const ts = data.tension || [];
      if(xs.length===0 || ts.length===0) return grp;
      const tmin = Math.min(...ts), tmax = Math.max(...ts);
      const scale = (tmax > tmin) ? 0.8/(tmax - tmin) : 0.0;
      for(let i=0; i<xs.length; i += Math.max(1, Math.floor(xs.length/12))){{
        const x = xs[i] - data.length/2;
        const h = (ts[i] - tmin)*scale + 0.2;
        const geo = new THREE.ConeGeometry(0.12, 0.4 + 0.8*h, 12);
        const mat = new THREE.MeshStandardMaterial();
        const a = new THREE.Mesh(geo, mat);
        a.position.set(x, data.height/2 + 0.6 + h, 0);
        a.rotation.z = Math.PI/2;
        grp.add(a);
      }}
      return grp;
    }}

    function buildProceduralConveyor(){{
      const thickness=0.08;
      const beltGeo = new THREE.BoxGeometry(data.length, thickness, data.width);
      const beltMat = new THREE.MeshStandardMaterial({{metalness:0.2, roughness:0.7}});
      const belt = new THREE.Mesh(beltGeo, beltMat);
      belt.position.y = data.height/2;
      rootGroup.add(belt);

      const rRoll = Math.max(0.05, data.width*0.03);
      const spacing = Math.max(0.6, data.idler_spacing);
      const n = Math.max(2, Math.floor(data.length/spacing));
      const zHalf = data.width/2*0.95;
      const centerY = data.height/2 - thickness/2 - rRoll*0.2;
      const ang = data.trough_deg * Math.PI/180;
      for(let i=0; i<=n; i++){{
        const x = -data.length/2 + i*spacing;
        rollers.push(makeRoller(rRoll, data.width*0.9, new THREE.Vector3(x, centerY, 0), 0));
        const sideLen = data.width*0.45;
        rollers.push(makeRoller(rRoll*0.98, sideLen, new THREE.Vector3(x, centerY, -zHalf),  ang));
        rollers.push(makeRoller(rRoll*0.98, sideLen, new THREE.Vector3(x, centerY,  zHalf), -ang));
      }}

      const pr = data.pulley_d/2.0;
      headPulley = makePulley(pr, data.width*0.95, new THREE.Vector3(+data.length/2 - pr, data.height/2, 0));
      tailPulley = makePulley(pr, data.width*0.95, new THREE.Vector3(-data.length/2 + pr, data.height/2, 0));

      // Fit camera to the whole procedural assembly
      fitCameraToObject(rootGroup);
    }}

    function loadReferenceGLB(url){{
      return new Promise((resolve,reject) => {{
        if (typeof THREE.GLTFLoader === 'undefined') {{
          reject(new Error('GLTFLoader not available'));
          return;
        }}
        try {{
          const loader = new THREE.GLTFLoader();
          loader.load(url, (gltf) => {{
            refModel = gltf.scene || gltf.scenes[0];
            refModel.traverse(o=>{{ if(o.isMesh) o.castShadow = o.receiveShadow = true; }});
            // Nghiêng theo góc dốc tổng thể (nếu cần)
            refModel.rotation.z = data.alpha;
            scene.add(refModel);

            // Fit camera/target đúng theo bounding box của GLB
            fitCameraToObject(refModel);
            resolve(true);
          }}, undefined, (err)=>reject(err));
        }} catch(err) {{
          reject(err);
        }}
      }});
    }}

    function buildScene(){{
      scene=new THREE.Scene();
      scene.background=new THREE.Color({ '0x0f172a' if self.theme=='dark' else '0xf8fafc' });

      camera=new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 5000);
      camera.position.set(8, 4, 8);

      renderer=new THREE.WebGLRenderer({{antialias:true}});
      renderer.setPixelRatio(devicePixelRatio);
      renderer.setSize(window.innerWidth, window.innerHeight);
      document.body.appendChild(renderer.domElement);

      scene.add(new THREE.AmbientLight(0xffffff, .7));
      const dir=new THREE.DirectionalLight(0xffffff, .8);
      dir.position.set(60,80,40);
      dir.castShadow=true;
      scene.add(dir);

      const grid=new THREE.GridHelper(200, 40);
      grid.position.y = -1;
      scene.add(grid);

      rootGroup=new THREE.Group();
      rootGroup.rotation.z = data.alpha;
      scene.add(rootGroup);

      // Initialize orbit params relative to initial camera/target
      const dx = camera.position.x - orbitTarget.x;
      const dy = camera.position.y - orbitTarget.y;
      const dz = camera.position.z - orbitTarget.z;
      orbitRadius = Math.sqrt(dx*dx + dy*dy + dz*dz);
      orbitTheta = Math.atan2(dz, dx);
      orbitPhi = Math.acos(THREE.MathUtils.clamp(dy/orbitRadius, -1, 1));
      updateCameraFromOrbit();

      // Mouse controls
      let state='idle', lastX=0, lastY=0;
      renderer.domElement.addEventListener('mousedown', (e)=>{{
        if(e.button===0) state = e.shiftKey ? 'pan':'rotate';
        if(e.button===1) state = 'pan';
        lastX = e.clientX; lastY = e.clientY;
      }});
      window.addEventListener('mouseup', ()=>state='idle');
      renderer.domElement.addEventListener('mousemove', (e)=>{{
        const dx=e.clientX-lastX, dy=e.clientY-lastY; lastX=e.clientX; lastY=e.clientY;
        if(state==='rotate'){{
          orbitTheta -= dx*0.005;
          orbitPhi   -= dy*0.005;
          updateCameraFromOrbit();
        }} else if(state==='pan'){{
          const panScale = orbitRadius * 0.0015;
          const ct=Math.cos(orbitTheta), st=Math.sin(orbitTheta), sp=Math.sin(orbitPhi), cp=Math.cos(orbitPhi);
          orbitTarget.x -= (dx*ct + dy*sp*st) * panScale;
          orbitTarget.z -= (-dx*st + dy*sp*ct) * panScale;
          orbitTarget.y += dy*cp * panScale;
          updateCameraFromOrbit();
        }}
      }});
      renderer.domElement.addEventListener('wheel', (e)=>{{
        e.preventDefault();
        orbitRadius *= (1 + (e.deltaY>0 ? 0.08 : -0.08));
        updateCameraFromOrbit();
      }}, {{passive:false}});
    }}

    function animate(){{
      requestAnimationFrame(animate);
      if(anim){{
        const wPulley = conveyorSpeed / Math.max(0.05, data.pulley_d/2);
        if(headPulley) headPulley.rotation.y += wPulley * 0.02;
        if(tailPulley) tailPulley.rotation.y += wPulley * 0.02;

        rollers.forEach(r => {{
          const rad = Math.max(0.05, r.userData.radius || 0.05);
          r.rotation.y += (conveyorSpeed / rad) * 0.02; // ω = v/r
        }});

        if(materialPts){{
          const pos = materialPts.geometry.attributes.position;
          for(let i=0; i<pos.count; i++){{
            let x = pos.getX(i) + conveyorSpeed*0.02;
            if(x > data.length/2) x = -data.length/2;
            pos.setX(i, x);
          }}
          pos.needsUpdate = true;
        }}
      }}
      renderer.render(scene, camera);
    }}

    function resize(){{
      camera.aspect = window.innerWidth/window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }}

    function resetCamera(){{
      // Fit theo rootGroup nếu có mô hình thủ công, còn có GLB thì fit theo GLB
      if(refModel) fitCameraToObject(refModel);
      else fitCameraToObject(rootGroup);
    }}

    function changeView(v){{
      // Giữ target, chỉ thay đổi vị trí camera theo preset
      const R = orbitRadius;
      if(v === 'top')      camera.position.set(orbitTarget.x, orbitTarget.y + R, orbitTarget.z);
      else if(v === 'side')  camera.position.set(orbitTarget.x + R, orbitTarget.y, orbitTarget.z);
      else if(v === 'front') camera.position.set(orbitTarget.x, orbitTarget.y, orbitTarget.z + R);
      else                   camera.position.set(orbitTarget.x + R*0.7, orbitTarget.y + R*0.5, orbitTarget.z + R*0.7);

      // Cập nhật tham số quỹ đạo tương ứng
      const dx=camera.position.x-orbitTarget.x, dy=camera.position.y-orbitTarget.y, dz=camera.position.z-orbitTarget.z;
      orbitRadius=Math.sqrt(dx*dx+dy*dy+dz*dz);
      orbitTheta=Math.atan2(dz,dx);
      orbitPhi=Math.acos(THREE.MathUtils.clamp(dy/orbitRadius,-1,1));
      updateCameraFromOrbit();
    }}

    async function init(){{
      if(!assertThree()) return;
      buildScene();

      let usedReference = false;
      if(data.modelUrl && data.modelUrl.length>0){{
        try {{
          await loadReferenceGLB(data.modelUrl);
          usedReference = true;
        }} catch(e){{
          console.warn('Không thể tải GLB tham chiếu (sẽ dùng mô hình thủ công):', e);
        }}
      }}

      if(!usedReference){{
        buildProceduralConveyor();
        materialPts = buildMaterial(); scene.add(materialPts);
        forceArrows = buildForcesFromProfile(); scene.add(forceArrows);
      }}

      window.addEventListener('resize', resize);
      animate();
    }}

    window.__setVisible = function(name, on) {{
      if(name === 'material' && materialPts) materialPts.visible = on;
      if(name === 'forces' && forceArrows)   forceArrows.visible = on;
    }};
    window.__setAnim = function(on)  {{ anim = !!on; }};
    window.__setSpeed = function(s)  {{ conveyorSpeed = Math.max(0.01, s); }};
    window.changeView = changeView;
    window.resetCamera = resetCamera;

    init();
    </script>
    """

    # -------------- Scene loader --------------
    def _load_scene(self) -> None:
        html = self._generate_html()
        if self._temp_html_file:
            try:
                path = self._temp_html_file.name
                self._temp_html_file.close()
                if os.path.exists(path):
                    os.unlink(path)
            except Exception:
                pass

        self._temp_html_file = tempfile.NamedTemporaryFile(
            "w", suffix=".html", delete=False, encoding="utf-8"
        )
        self._temp_html_file.write(html)
        self._temp_html_file.flush()
        self._temp_html_file.close()
        self.web.load(QUrl.fromLocalFile(self._temp_html_file.name))

    # -------------- Public API --------------
    def update_visualization(self, params, result, theme: str = "light") -> None:
        self.current_params = params
        self.current_result = result
        self.theme = theme
        self._load_scene()

    # -------------- Slots --------------
    @Slot(bool)
    def _toggle_anim(self, checked: bool) -> None:
        self.web.page().runJavaScript(f"window.__setAnim({str(checked).lower()});")

    @Slot(bool)
    def _toggle_material(self, checked: bool) -> None:
        self.web.page().runJavaScript(
            f"window.__setVisible('material', {str(checked).lower()});"
        )

    @Slot(bool)
    def _toggle_forces(self, checked: bool) -> None:
        self.web.page().runJavaScript(
            f"window.__setVisible('forces', {str(checked).lower()});"
        )

    @Slot(bool)
    def _toggle_heat(self, checked: bool) -> None:
        js = f"""
        (function(on){{
          if(!window.rootGroup||!window.rootGroup.children) return;
          const belt = window.rootGroup.children.find(m => m.geometry && m.geometry.type==='BoxGeometry');
          if(!belt) return;
          belt.material.color.setHex(on ? 0xff6b6b : 0x2c3e50);
        }})(%s);
        """ % (
            str(checked).lower()
        )
        self.web.page().runJavaScript(js)

    @Slot(str)
    def _change_view(self, name: str) -> None:
        mapping = {
            "Isometric": "default",
            "Top View": "top",
            "Side View": "side",
            "Front View": "front",
        }
        key = mapping.get(name, "default")
        self.web.page().runJavaScript(f"window.changeView('{key}');")

    @Slot(int)
    def _change_speed(self, value: int) -> None:
        speed = round(0.1 + (value - 1) * (4.9 / 99.0), 3)
        self.web.page().runJavaScript(f"window.__setSpeed({speed});")

    @Slot()
    def _reset_cam(self) -> None:
        self.web.page().runJavaScript("window.resetCamera();")

    @Slot()
    def _toggle_fullscreen(self) -> None:
        win = self.window()
        if not self._is_fullscreen:
            self._saved_geometry = win.saveGeometry()
            self._saved_window_state = win.windowState()
            win.showFullScreen()
            self._is_fullscreen = True
            self.btn_full.setText("Thoát toàn màn hình")
        else:
            try:
                win.showNormal()
                if self._saved_geometry:
                    win.restoreGeometry(self._saved_geometry)
                if self._saved_window_state is not None:
                    win.setWindowState(self._saved_window_state)
            except Exception:
                pass
            self._is_fullscreen = False
            self.btn_full.setText("Toàn màn hình 3D")

    @Slot()
    def _screenshot(self) -> None:
        try:
            pix: QPixmap = self.web.grab()
            if pix.isNull():
                QMessageBox.warning(
                    self,
                    "Chụp ảnh 3D",
                    "Không thể chụp ảnh. Hãy thử lại sau khi scene đã tải xong.",
                )
                return
            path, _ = QFileDialog.getSaveFileName(
                self, "Lưu ảnh 3D", "conveyor_3d.png", "PNG (*.png)"
            )
            if not path:
                return
            pix.save(path, "PNG")
            QMessageBox.information(self, "Chụp ảnh 3D", f"Đã lưu ảnh: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Chụp ảnh 3D", f"Lỗi khi chụp: {e}")