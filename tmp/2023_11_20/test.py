import sys
from lets_plot import *
from PyQt6.QtWidgets import QApplication
from PyQt6.QtSvgWidgets import QSvgWidget

app = QApplication(sys.argv)
p = ggplot() + geom_point(x=0, y=0)
path = ggsave(p, 'p.svg')
svgWidget = QSvgWidget(path)
svgWidget.setGeometry(0, 0, 640, 480)
svgWidget.show()

sys.exit(app.exec())