# Copilot: Implement strictly per comments.
# Do NOT reference or display the original PDF name or path anywhere in UI or logs.
# Citations must be anonymous: {"page": int, "section": str|None}.
# Build-time uses PDF, runtime uses only the persisted index.

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QTextEdit, QPushButton, QListWidget,
                           QListWidgetItem, QLabel, QCheckBox,
                           QSizePolicy, QProgressBar)
from PySide6.QtCore import Qt, QTimer, QEvent, QDateTime
from PySide6.QtGui import QMovie
import os
from core.ai.chat_service import ChatService
from core.rag.index import load_index

class MessageWidget(QWidget):
    def __init__(self, text: str, is_user=False):
        super().__init__()
        layout = QVBoxLayout()
        
        # Message text
        message = QLabel(text)
        message.setWordWrap(True)
        message.setStyleSheet(
            "background-color: #e3f2fd;" if is_user else "background-color: #f5f5f5;"
        )
        layout.addWidget(message)
        
        self.setLayout(layout)

class ChatPanel(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize chat history
        self.history = []
        
        # Setup UI first
        self.setup_ui()
        
        # Setup chat service
        self.setup_chat_service()
    
    def setup_chat_service(self):
        """Initialize chat service with index."""
        try:
            index_dir = os.getenv('INDEX_DIR')
            if not index_dir:
                print("Warning: INDEX_DIR environment variable not set")
                print("Creating basic chat service without RAG capabilities")
                self.chat_service = ChatService(None)
                return
            
            # Kiểm tra xem thư mục index có tồn tại không
            if not os.path.exists(index_dir):
                print(f"Warning: INDEX_DIR does not exist: {index_dir}")
                print("Creating basic chat service without RAG capabilities")
                self.chat_service = ChatService(None)
                return
            
            # Kiểm tra xem file chunks.faiss có tồn tại không
            faiss_file = os.path.join(index_dir, "chunks.faiss")
            if not os.path.exists(faiss_file):
                print(f"Warning: chunks.faiss file not found in: {index_dir}")
                print("Creating basic chat service without RAG capabilities")
                self.chat_service = ChatService(None)
                return
                
            print(f"Loading index from: {index_dir}")
            retriever = load_index(index_dir)
            self.chat_service = ChatService(retriever)
            print("RAG-enabled chat service initialized successfully")
            
        except Exception as e:
            print(f"Error setting up chat service: {e}")
            print("Falling back to basic chat service without RAG capabilities")
            self.chat_service = ChatService(None)
        
        # Thông báo trạng thái cuối cùng
        if self.chat_service.retriever is None:
            print("Chat service initialized in basic mode (no RAG)")
        else:
            print("Chat service initialized in RAG mode")
    
    def add_message(self, role: str, content: str):
        """Add a message to the chat display."""
        try:
            if isinstance(self.messages, QListWidget):
                # Use MessageWidget for QListWidget
                message_widget = MessageWidget(content, is_user=(role == "user"))
                item = QListWidgetItem(self.messages)
                item.setSizeHint(message_widget.sizeHint())
                self.messages.addItem(item)
                self.messages.setItemWidget(item, message_widget)
                
                # Scroll to bottom
                self.messages.scrollToBottom()
            elif hasattr(self.messages, 'toPlainText'):
                # Use simple text for QTextEdit fallback
                current_text = self.messages.toPlainText()
                timestamp = QDateTime.currentDateTime().toString("HH:mm")
                new_message = f"[{timestamp}] {role.upper()}: {content}\n"
                self.messages.setPlainText(current_text + new_message)
                
                # Scroll to bottom
                cursor = self.messages.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                self.messages.setTextCursor(cursor)
            else:
                # For QLabel fallback, just update the text
                current_text = self.messages.text()
                timestamp = QDateTime.currentDateTime().toString("HH:mm")
                new_message = f"[{timestamp}] {role.upper()}: {content}\n"
                self.messages.setText(current_text + new_message)
            
            # Add to history for chat service
            self.history.append({"role": role, "content": content})
        except Exception as e:
            print(f"Error adding message: {e}")
            # Final fallback: print to console
            print(f"[{role.upper()}]: {content}")
    
    def setup_ui(self):
        """Setup the chat interface."""
        # Set size policy for the main widget
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Set minimum size
        self.setMinimumSize(400, 300)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(0)  # Remove spacing between elements
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header with title
        header = QWidget()
        header.setFixedHeight(40)  # Fixed header height
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel("💬 Trợ lý kỹ thuật")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2563eb;")
        header_layout.addWidget(title)
        layout.addWidget(header)

        # Messages container
        messages_container = QWidget()
        messages_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        messages_layout = QVBoxLayout(messages_container)
        messages_layout.setContentsMargins(0, 5, 0, 5)  # Add small vertical padding
        messages_layout.setSpacing(0)
        
        # Messages area
        try:
            self.messages = QListWidget()
            self.messages.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            self.messages.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.messages.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
            self.messages.setHorizontalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        except Exception as e:
            print(f"Error creating messages widget: {e}")
            # Fallback: create simple text area
            try:
                self.messages = QTextEdit()
                self.messages.setReadOnly(True)
                print("Using fallback text area for messages")
            except Exception as fallback_error:
                print(f"Error creating fallback text area: {fallback_error}")
                # Final fallback: create simple label
                self.messages = QLabel("Messages will be displayed here")
                self.messages.setWordWrap(True)
                print("Using simple label for messages")
        
        messages_layout.addWidget(self.messages)
        
        # Loading indicator and progress bar container
        status_container = QWidget()
        status_layout = QVBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(2)
        
        self.loading_label = QLabel("Đang xử lý...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: #2563eb;
                font-style: italic;
                background-color: #e5e7eb;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        self.loading_label.hide()
        status_layout.addWidget(self.loading_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(2)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #e5e7eb;
            }
            QProgressBar::chunk {
                background-color: #2563eb;
            }
        """)
        self.progress_bar.hide()
        status_layout.addWidget(self.progress_bar)
        
        messages_layout.addWidget(status_container)
        layout.addWidget(messages_container, 1)
        
        # Add loading indicators
        layout.addWidget(self.loading_label)
        layout.addWidget(self.progress_bar)
        
        # Style the messages widget
        self.messages.setStyleSheet("""
            QListWidget {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background-color: #ffffff;
            }
            QListWidget::item {
                padding: 5px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #888;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical {
                height: 0px;
            }
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: #f1f1f1;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #888;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal {
                width: 0px;
            }
            QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        # Input area container
        input_container = QWidget()
        input_container.setFixedHeight(120)  # Fixed height for input area
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 5, 0, 0)  # Add top padding
        
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Nhập câu hỏi của bạn... (Nhấn Enter để gửi)")
        self.input_box.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 8px;
                background-color: #ffffff;
            }
        """)
        # Handle Enter key press
        try:
            self.input_box.installEventFilter(self)
            self._event_filter_installed = True
        except Exception as e:
            print(f"Warning: Could not install event filter: {e}")
            # Fallback: connect to button click only
            self._event_filter_installed = False
        input_layout.addWidget(self.input_box)
        
        self.send_button = QPushButton("Gửi")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        # Fallback: if event filter fails, ensure button works
        if not hasattr(self, '_event_filter_installed') or not self._event_filter_installed:
            print("Event filter not installed, button click is the only way to send messages")
        layout.addWidget(input_container)  # Add fixed-height input container
        self.setLayout(layout)
        
        # Add welcome message
        try:
            if isinstance(self.messages, QListWidget):
                welcome_msg = MessageWidget(
                    "Xin chào! Tôi là trợ lý kỹ thuật. Tôi có thể giúp bạn với các câu hỏi về thiết kế và tính toán băng tải."
                )
                item = QListWidgetItem(self.messages)
                item.setSizeHint(welcome_msg.sizeHint())
                self.messages.addItem(item)
                self.messages.setItemWidget(item, welcome_msg)
            else:
                # For QTextEdit fallback
                welcome_text = "Xin chào! Tôi là trợ lý kỹ thuật. Tôi có thể giúp bạn với các câu hỏi về thiết kế và tính toán băng tải."
                self.messages.setPlainText(welcome_text)
        except Exception as e:
            print(f"Error creating welcome message: {e}")
            # Fallback: add simple welcome message
            if isinstance(self.messages, QListWidget):
                welcome_item = QListWidgetItem("[ASSISTANT]: Xin chào! Tôi là trợ lý kỹ thuật. Tôi có thể giúp bạn với các câu hỏi về thiết kế và tính toán băng tải.")
                self.messages.addItem(welcome_item)
            else:
                self.messages.setPlainText("[ASSISTANT]: Xin chào! Tôi là trợ lý kỹ thuật. Tôi có thể giúp bạn với các câu hỏi về thiết kế và tính toán băng tải.")
    
    def eventFilter(self, obj, event):
        """Handle Enter key press in input box."""
        if not hasattr(self, '_event_filter_installed') or not self._event_filter_installed:
            return super().eventFilter(obj, event)
            
        if obj == self.input_box and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not event.modifiers():
                # Enter without modifier keys
                self.send_message()
                return True
            elif event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                # Shift+Enter for new line
                self.input_box.insertPlainText("\n")
                return True
        return super().eventFilter(obj, event)
    
    def send_message(self):
        """Send the current message."""
        message = self.input_box.toPlainText().strip()
        if not message:
            return
            
        # Clear input field
        self.input_box.clear()
        
        # Add user message to chat
        self.add_message("user", message)
        
        # Show loading indicator
        self.loading_label.show()
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Process message in background
        try:
            # Get response from chat service (pass history without the current user message)
            current_history = self.history[:-1]  # Exclude the current user message
            response = self.chat_service.ask(message, history=current_history)
            answer = response.get("answer", "Xin lỗi, tôi không thể trả lời câu hỏi này.")
            
            # Add assistant response
            self.add_message("assistant", answer)
            
        except Exception as e:
            error_msg = f"Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn: {str(e)}"
            self.add_message("assistant", error_msg)
            print(f"Error in send_message: {e}")
        
        finally:
            # Hide loading indicators
            self.loading_label.hide()
            self.progress_bar.hide()
