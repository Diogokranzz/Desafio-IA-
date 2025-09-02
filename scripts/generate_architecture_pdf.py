import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm


def draw_box(c, x, y, w, h, text):
    c.setStrokeColor(colors.HexColor("#333333"))
    c.setFillColor(colors.HexColor("#F2F2F2"))
    c.rect(x, y, w, h, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x + w / 2, y + h / 2 - 5, text)


def draw_arrow(c, x1, y1, x2, y2):
    c.setStrokeColor(colors.HexColor("#777777"))
    c.line(x1, y1, x2, y2)
    c.line(x2, y2, x2 - 5, y2 + 5)
    c.line(x2, y2, x2 - 5, y2 - 5)


def main():
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from src.config import REPORTS_DIR  # import local após ajuste do sys.path

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / "architecture.pdf"

    c = canvas.Canvas(str(out), pagesize=A4)
    width, height = A4

    agent_x, agent_y, agent_w, agent_h = 9 * cm, 24 * cm, 8 * cm, 2 * cm
    tools_y = 18 * cm

    draw_box(c, agent_x, agent_y, agent_w, agent_h, "Orquestrador")

    tool_boxes = [
        (2 * cm, tools_y, 6 * cm, 2 * cm, "Métricas (CSV/BD)"),
        (9 * cm, tools_y, 6 * cm, 2 * cm, "Notícias (RSS/Web)"),
        (16 * cm, tools_y, 6 * cm, 2 * cm, "Consulta local (opcional)"),
    ]

    for x, y, w, h, label in tool_boxes:
        draw_box(c, x, y, w, h, label)
        draw_arrow(c, x + w / 2, y + h, agent_x + agent_w / 2, agent_y)
        draw_arrow(c, agent_x + agent_w / 2, agent_y, x + w / 2, y + h)

    src_y = 12 * cm
    src_boxes = [
        (2 * cm, src_y, 8 * cm, 2 * cm, "OpenDataSUS – SRAG CSV"),
        (12 * cm, src_y, 10 * cm, 2 * cm, "Sites de notícias / Google News RSS"),
    ]

    for x, y, w, h, label in src_boxes:
        draw_box(c, x, y, w, h, label)

    out_y = 6 * cm
    out_boxes = [
        (4 * cm, out_y, 8 * cm, 2 * cm, "Relatório em Markdown + Gráficos"),
        (14 * cm, out_y, 8 * cm, 2 * cm, "Diagrama de arquitetura (PDF)"),
    ]

    for x, y, w, h, label in out_boxes:
        draw_box(c, x, y, w, h, label)

    draw_arrow(c, 6 * cm, src_y + 2 * cm, 5 * cm, tools_y)
    draw_arrow(c, 17 * cm, src_y + 2 * cm, 12 * cm, tools_y)

    draw_arrow(c, agent_x + agent_w / 2, agent_y, 8 * cm, out_y + 2 * cm)
    draw_arrow(c, agent_x + agent_w / 2, agent_y, 18 * cm, out_y + 2 * cm)

    c.showPage()
    c.save()
    print(f"Salvo em: {out}")


if __name__ == "__main__":
    main()
