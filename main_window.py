import sys
import asyncio
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, 
    QListWidget, QTextEdit, QLabel, QSplitter, QFrame, QScrollArea, QSizePolicy, 
    QFileDialog, QComboBox, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
from qasync import QEventLoop, asyncSlot

from crawler.news_crawler import NewsCrawler
from llm.llm_handler import LLMHandler
from utils.exporters import Exporters

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EIDOS News Aggregator")
        self.setGeometry(100, 100, 1200, 800)

        self.crawler = NewsCrawler()
        
        # [!!! 수정 시작 !!!]
        try:
            self.llm_handler = LLMHandler()
            self.llm_ready = True
        except ValueError as e:
            # API 키가 없을 때 발생하는 오류를 잡습니다.
            self.llm_handler = None
            self.llm_ready = False
            logging.error(f"LLM 초기화 실패: {e}")
            # 사용자에게 친절하게 알림
            QMessageBox.critical(self, "API 키 오류", 
                "OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.\n\n"
                "뉴스 요약, 키워드 추출, 분류 기능이 비활성화됩니다.\n"
                "API 키를 설정한 후 프로그램을 다시 시작하세요.")
        # [!!! 수정 끝 !!!]
            
        self.articles = [] 
        self.current_theme = 'dark'

        self.init_ui()
        self.apply_stylesheet('dark')
        
        # [!!! 수정 !!!] LLM이 준비되지 않았다면 버튼 비활성화
        if not self.llm_ready:
            self.fetch_button.setEnabled(False)
            self.fetch_button.setText("API 키 필요")
            self.fetch_button.setToolTip("OPENAI_API_KEY 환경 변수를 설정하세요.")

    def init_ui(self):
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top bar
        top_bar_layout = QHBoxLayout()
        self.fetch_button = QPushButton("뉴스 가져오기")
        self.fetch_button.clicked.connect(self.fetch_and_update)
        self.theme_switch = QPushButton("Toggle Theme")
        self.theme_switch.clicked.connect(self.toggle_theme)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        top_bar_layout.addWidget(self.fetch_button)
        top_bar_layout.addStretch(1)
        top_bar_layout.addWidget(self.progress_bar)
        top_bar_layout.addWidget(self.theme_switch)
        main_layout.addLayout(top_bar_layout)

        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel (Categories)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("Categories"))
        self.category_list = QListWidget()
        self.category_list.itemClicked.connect(self.filter_by_category)
        left_layout.addWidget(self.category_list)
        splitter.addWidget(left_panel)

        # Right panel (Articles and details)
        right_panel = QSplitter(Qt.Vertical)
        
        self.article_list = QListWidget()
        self.article_list.itemClicked.connect(self.display_article_details)
        
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        self.article_title = QLabel("Select an article to see details")
        self.article_title.setWordWrap(True)
        self.article_summary = QTextEdit()
        self.article_summary.setReadOnly(True)
        self.keyword_container = QWidget()
        self.keyword_layout = QHBoxLayout(self.keyword_container)
        self.keyword_layout.setAlignment(Qt.AlignLeft)
        detail_layout.addWidget(self.article_title)
        detail_layout.addWidget(self.article_summary)
        detail_layout.addWidget(self.keyword_container)

        # Export section
        export_layout = QHBoxLayout()
        self.export_combo = QComboBox()
        self.export_combo.addItems(["CSV", "TXT", "PDF"])
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_data)
        export_layout.addWidget(QLabel("Export as:"))
        export_layout.addWidget(self.export_combo)
        export_layout.addWidget(self.export_button)
        detail_layout.addLayout(export_layout)

        right_panel.addWidget(self.article_list)
        right_panel.addWidget(detail_widget)
        right_panel.setSizes([400, 400])

        splitter.addWidget(right_panel)
        splitter.setSizes([200, 1000])

    def apply_stylesheet(self, theme='dark'):
        if theme == 'dark':
            self.setStyleSheet("""
                QWidget { background-color: #2b2b2b; color: #f0f0f0; }
                QPushButton { background-color: #4a4a4a; border: 1px solid #6a6a6a; padding: 5px; }
                QPushButton:hover { background-color: #5a5a5a; }
                QListWidget { background-color: #3c3c3c; border: 1px solid #5a5a5a; }
                QTextEdit { background-color: #3c3c3c; border: 1px solid #5a5a5a; }
                QLabel { color: #f0f0f0; }
                QComboBox { background-color: #3c3c3c; border: 1px solid #5a5a5a; }
            """)
        else: # light
            self.setStyleSheet("""
                QWidget { background-color: #f0f0f0; color: #2b2b2b; }
                QPushButton { background-color: #e1e1e1; border: 1px solid #c1c1c1; padding: 5px; }
                QPushButton:hover { background-color: #d1d1d1; }
                QListWidget { background-color: #ffffff; border: 1px solid #c1c1c1; }
                QTextEdit { background-color: #ffffff; border: 1px solid #c1c1c1; }
                QLabel { color: #2b2b2b; }
                QComboBox { background-color: #ffffff; border: 1px solid #c1c1c1; }
            """)

    def toggle_theme(self):
        if self.current_theme == 'dark':
            self.current_theme = 'light'
            self.apply_stylesheet('light')
        else:
            self.current_theme = 'dark'
            self.apply_stylesheet('dark')

    @asyncSlot()
    async def fetch_and_update(self):
        self.fetch_button.setEnabled(False)
        self.fetch_button.setText("Fetching...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0) # Indeterminate progress
        
        try:
            crawled_articles = await self.crawler.crawl()
            if not crawled_articles:
                logging.warning("No articles were crawled.")
                return

            self.progress_bar.setRange(0, len(crawled_articles))
            processed_articles = []
            for i, article in enumerate(crawled_articles):
                self.fetch_button.setText(f"Analyzing {i+1}/{len(crawled_articles)}")
                article['summary'] = await self.llm_handler.summarize_text(article['content'])
                article['keywords'] = await self.llm_handler.extract_keywords(article['content'])
                article['category'] = await self.llm_handler.classify_category(article['content'])
                processed_articles.append(article)
                self.progress_bar.setValue(i + 1)

            self.articles = processed_articles
            self.update_ui_with_articles(self.articles)
        except Exception as e:
            logging.error(f"An error occurred during fetch and update: {e}")
        finally:
            self.fetch_button.setEnabled(True)
            self.fetch_button.setText("뉴스 가져오기")
            self.progress_bar.setVisible(False)

    def update_ui_with_articles(self, articles_to_display):
        self.update_article_list(articles_to_display)
        self.update_categories(self.articles) # Always update categories based on the full list

    def update_article_list(self, articles):
        self.article_list.clear()
        for article in articles:
            self.article_list.addItem(article['title'])

    def update_categories(self, articles):
        self.category_list.clear()
        self.category_list.addItem("All")
        categories = sorted(list(set(article['category'] for article in articles)))
        self.category_list.addItems(categories)

    def display_article_details(self, item):
        title = item.text()
        article = next((a for a in self.articles if a['title'] == title), None)
        if article:
            self.article_title.setText(article['title'])
            self.article_summary.setText(article['summary'])
            # Clear old keywords
            for i in reversed(range(self.keyword_layout.count())):
                self.keyword_layout.itemAt(i).widget().setParent(None)
            # Add new keywords
            for keyword in article.get('keywords', []):
                keyword_button = QPushButton(keyword)
                keyword_button.clicked.connect(lambda _, k=keyword: self.filter_by_keyword(k))
                self.keyword_layout.addWidget(keyword_button)

    def filter_by_category(self, item):
        category = item.text()
        if category == "All":
            self.update_article_list(self.articles)
        else:
            filtered = [a for a in self.articles if a['category'] == category]
            self.update_article_list(filtered)

    def filter_by_keyword(self, keyword):
        filtered = [a for a in self.articles if keyword in a.get('keywords', [])]
        self.update_article_list(filtered)
        # DO NOT update categories here to maintain UX consistency.

    def export_data(self):
        file_format = self.export_combo.currentText().lower()
        default_filename = f"news_export.{file_format}"
        filepath, _ = QFileDialog.getSaveFileName(self, "Save File", default_filename, f"{file_format.upper()} Files (*.{file_format});;All Files (*)")

        if filepath:
            current_articles_on_display = []
            for i in range(self.article_list.count()):
                title = self.article_list.item(i).text()
                article = next((a for a in self.articles if a['title'] == title), None)
                if article:
                    current_articles_on_display.append(article)
            
            if not current_articles_on_display:
                return

            if file_format == 'csv':
                Exporters.to_csv(current_articles_on_display, filepath)
            elif file_format == 'txt':
                Exporters.to_txt(current_articles_on_display, filepath)
            elif file_format == 'pdf':
                Exporters.to_pdf(current_articles_on_display, filepath)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    main_win = MainWindow()
    main_win.show()

    with loop:
        loop.run_forever()
