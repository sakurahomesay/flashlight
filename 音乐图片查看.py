import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout, QScrollArea, QWidgetItem
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QImage, QPixmap
from PIL import Image as PilImage
import mutagen

class DragDropWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('音乐图片查看')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Scrollable area for cards
        scroll_area = QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("border: none;")  # Remove border
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(3)  # Set spacing between cards to 3 pixels
        self.grid_layout.setContentsMargins(15, 15, 15, 15)  # Set margins for content
        self.scroll_content.setLayout(self.grid_layout)
        scroll_area.setWidgetResizable(True)  # Ensure the widget resizes with the scroll area
        scroll_area.setWidget(self.scroll_content)

        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

        # Set the entire window to accept drops
        self.setAcceptDrops(True)

        # Track the number of cards added
        self.card_count = 0

    def dragEnterEvent(self, event):
        print("Drag enter event triggered")
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        print("Drag move event triggered")
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        print("Drop event triggered")
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            print(f"Dropped file path: {file_path}")
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                card_widget = self.create_image_card(file_path)
            elif file_path.lower().endswith(('.mp3', '.wma', '.ape', '.flac', '.aac', '.ac3', '.m4a', '.m4r', '.ogg', '.wav')):
                card_widget = self.create_audio_card(file_path)
            else:
                print(f"Unsupported file format: {file_path}")
                continue
            if card_widget is not None:
                row = self.card_count // 4  # Assuming 4 cards per row
                col = self.card_count % 4
                self.grid_layout.addWidget(card_widget, row, col)
                self.card_count += 1
        event.acceptProposedAction()

    def create_image_card(self, file_path):
        try:
            # Ensure file path is properly encoded
            file_path = os.path.normpath(file_path)

            # Check if file exists
            if not os.path.exists(file_path):
                print(f"File does not exist: {file_path}")
                return None

            # Load image using QPixmap
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                print(f"Failed to load image using QPixmap: {file_path}")
                return None

            # Verify image can be opened by PIL
            try:
                with PilImage.open(file_path) as img:
                    resolution = f"分辨率: {img.width}x{img.height}"
                    file_size_bytes = os.path.getsize(file_path)
                    file_size_mb = f"大小: {file_size_bytes / (1024 * 1024):.2f} MB"
                    format_info = f"格式: {img.format}"
            except Exception as e:
                print(f"Failed to open image using PIL: {file_path}, Error: {e}")
                return None

            card_widget = QWidget()
            card_layout = QVBoxLayout(card_widget)
            card_layout.setContentsMargins(10, 10, 10, 10)  # Set margins inside card

            # File name (show last few characters without extension)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            if len(base_name) > 15:
                file_name_label = QLabel(f"...{base_name[-12:]}", card_widget)
            else:
                file_name_label = QLabel(base_name, card_widget)
            file_name_label.setAlignment(Qt.AlignCenter)
            file_name_label.setStyleSheet("font-weight: bold;")
            card_layout.addWidget(file_name_label)

            # Image preview
            label = QLabel(card_widget)
            scaled_pixmap = pixmap.scaledToWidth(100, Qt.SmoothTransformation)  # Set image width to 100px
            label.setPixmap(scaled_pixmap)
            card_layout.addWidget(label)
            print(f"Loaded image size: {scaled_pixmap.size()}")

            # Image information
            info_label = QLabel(f"{resolution}\n{file_size_mb}\n{format_info}", card_widget)
            info_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(info_label)

            # Apply styles
            card_widget.setStyleSheet("""
                background-color: white;
                border-radius: 10px;
                max-width: 130px; /* Increase card width slightly */
                max-height: 170px; /* Limit card height to slightly more than image */
            """)
            return card_widget
        except Exception as e:
            print(f"Error creating card for {file_path}: {e}")
            return None

    def create_audio_card(self, file_path):
        try:
            # Ensure file path is properly encoded
            file_path = os.path.normpath(file_path)

            # Check if file exists
            if not os.path.exists(file_path):
                print(f"File does not exist: {file_path}")
                return None

            # Load audio metadata using mutagen
            try:
                audio = mutagen.File(file_path)
                if audio is None:
                    raise ValueError("Unable to read audio metadata.")
                
                # Extract metadata
                bitrate = getattr(audio.info, 'bitrate', 'N/A')
                sample_rate = getattr(audio.info, 'sample_rate', 'N/A')
                file_size_bytes = os.path.getsize(file_path)
                file_size_mb = f"大小: {file_size_bytes / (1024 * 1024):.2f} MB"
                format_info = f"格式: {audio.mime[0]}"
                
                if isinstance(bitrate, tuple):
                    bitrate = bitrate[0]  # Some formats provide bitrate as a tuple
                
                bitrate_str = f"码率: {bitrate / 1000:.2f} kbps" if bitrate != 'N/A' else "码率: N/A"
                sample_rate_str = f"采样率: {sample_rate} Hz" if sample_rate != 'N/A' else "采样率: N/A"
            except Exception as e:
                print(f"Failed to extract audio metadata: {file_path}, Error: {e}")
                return None

            # Try to get embedded cover art
            icon_pixmap = None
            if isinstance(audio, mutagen.mp3.MP3):
                id3 = audio.tags
                if id3 is not None:
                    apic_frames = id3.getall('APIC')
                    if apic_frames:
                        apic_frame = apic_frames[0]
                        icon_pixmap = QPixmap()
                        icon_pixmap.loadFromData(apic_frame.data)
            elif isinstance(audio, mutagen.id3.ID3):
                apic_frames = audio.getall('APIC')
                if apic_frames:
                    apic_frame = apic_frames[0]
                    icon_pixmap = QPixmap()
                    icon_pixmap.loadFromData(apic_frame.data)
            elif isinstance(audio, mutagen.flac.FLAC):
                pictures = audio.pictures
                if pictures:
                    picture = pictures[0].data
                    icon_pixmap = QPixmap()
                    icon_pixmap.loadFromData(picture)
            elif isinstance(audio, mutagen.ogg.OggVorbis):
                pics = audio.tags.get('METADATA_BLOCK_PICTURE')
                if pics:
                    pic_data = pics[0]
                    import base64
                    pic_data_decoded = base64.b64decode(pic_data)
                    # Decode the vorbis comment data
                    offset = 0
                    while offset < len(pic_data_decoded):
                        length = int.from_bytes(pic_data_decoded[offset:offset+4], byteorder='big')
                        offset += 4
                        mime_type_length = int.from_bytes(pic_data_decoded[offset:offset+4], byteorder='big')
                        offset += 4
                        mime_type = pic_data_decoded[offset:offset+mime_type_length].decode('utf-8')
                        offset += mime_type_length
                        description_length = int.from_bytes(pic_data_decoded[offset:offset+4], byteorder='big')
                        offset += 4
                        description = pic_data_decoded[offset:offset+description_length].decode('utf-8')
                        offset += description_length
                        width = int.from_bytes(pic_data_decoded[offset:offset+4], byteorder='big')
                        offset += 4
                        height = int.from_bytes(pic_data_decoded[offset:offset+4], byteorder='big')
                        offset += 4
                        color_depth = int.from_bytes(pic_data_decoded[offset:offset+4], byteorder='big')
                        offset += 4
                        colors_used = int.from_bytes(pic_data_decoded[offset:offset+4], byteorder='big')
                        offset += 4
                        picture_data_length = int.from_bytes(pic_data_decoded[offset:offset+4], byteorder='big')
                        offset += 4
                        picture_data = pic_data_decoded[offset:offset+picture_data_length]
                        offset += picture_data_length
                        icon_pixmap = QPixmap()
                        icon_pixmap.loadFromData(picture_data)
            elif isinstance(audio, mutagen.wave.WAVE):
                pass  # WAV doesn't support embedded covers directly via mutagen

            if icon_pixmap is None or icon_pixmap.isNull():
                icon_pixmap = QPixmap(":/icons/audio_icon.png")  # Placeholder for an actual audio icon
                if icon_pixmap.isNull():
                    icon_pixmap = QPixmap(100, 100)
                    icon_pixmap.fill(Qt.lightGray)

            card_widget = QWidget()
            card_layout = QVBoxLayout(card_widget)
            card_layout.setContentsMargins(10, 10, 10, 10)  # Set margins inside card

            # File name (show last few characters without extension)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            if len(base_name) > 15:
                file_name_label = QLabel(f"...{base_name[-12:]}", card_widget)
            else:
                file_name_label = QLabel(base_name, card_widget)
            file_name_label.setAlignment(Qt.AlignCenter)
            file_name_label.setStyleSheet("font-weight: bold;")
            card_layout.addWidget(file_name_label)

            # Icon for audio files
            icon_label = QLabel(card_widget)
            icon_label.setPixmap(icon_pixmap.scaledToWidth(100, Qt.SmoothTransformation))
            card_layout.addWidget(icon_label)

            # Audio information
            info_label = QLabel(f"{bitrate_str}\n{sample_rate_str}\n{file_size_mb}\n{format_info}", card_widget)
            info_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(info_label)

            # Apply styles
            card_widget.setStyleSheet("""
                background-color: white;
                border-radius: 10px;
                max-width: 130px; /* Increase card width slightly */
                max-height: 170px; /* Limit card height to slightly more than image */
            """)
            return card_widget
        except Exception as e:
            print(f"Error creating card for {file_path}: {e}")
            return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DragDropWidget()
    ex.show()
    sys.exit(app.exec_())



