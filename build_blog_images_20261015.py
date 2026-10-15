#!/usr/bin/env python3
"""블로그 5포 이미지 합성 (2026-10-15): 썸네일 글자 합성 + 표·카드 제작.

원칙: 한글·수치는 생성형이 아닌 확정값 합성으로만 넣는다.
사양: ~/workspace/goals/2/files/images/20261015/spec-adjusted.md
"""
from PIL import Image, ImageDraw, ImageFont
import glob
import os

BASE = os.path.expanduser("~/workspace/goals/2/files/images/20261015")
BOLD_TTC = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
REG_TTC = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

NAVY = (18, 44, 74)
NAVY_LIGHT = (35, 74, 114)
WHITE = (255, 255, 255)
INK = (26, 32, 40)
GRAY = (96, 108, 122)
LINE = (214, 221, 230)
RED = (203, 52, 44)
BG_SOFT = (244, 247, 250)
GOLD = (255, 209, 102)


def kr_index(path):
    for i in range(12):
        try:
            name = ImageFont.truetype(path, 40, index=i).getname()[0]
            if "KR" in name:
                return i
        except Exception:
            break
    return 0


BOLD_I = kr_index(BOLD_TTC)
REG_I = kr_index(REG_TTC)


def font(path, size, idx):
    return ImageFont.truetype(path, size, index=idx)


def bold(size):
    return font(BOLD_TTC, size, BOLD_I)


def reg(size):
    return font(REG_TTC, size, REG_I)


def text_size(draw, s, f):
    box = draw.textbbox((0, 0), s, font=f)
    return box[2] - box[0], box[3] - box[1]


def cover(img, w, h):
    sw, sh = img.size
    scale = max(w / sw, h / sh)
    img = img.resize((int(sw * scale + 0.5), int(sh * scale + 0.5)), Image.LANCZOS)
    x = (img.size[0] - w) // 2
    y = (img.size[1] - h) // 2
    return img.crop((x, y, x + w, y + h))


def make_thumbnail(post_dir, big_lines, sub, accent=GOLD):
    bgs = glob.glob(os.path.join(BASE, post_dir, "media-generation-thumb-bg-*.webp"))
    if not bgs:
        print(f"SKIP {post_dir}: no bg")
        return None
    img = Image.open(bgs[0]).convert("RGB")
    img = cover(img, 1200, 1200)  # 썸네일 1:1 비율 (2026-10-16 사용자 지시)
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    draw = ImageDraw.Draw(img)
    big_f = bold(96)
    sub_f = bold(42)
    lines_w = max(text_size(draw, s, big_f)[0] for s in big_lines)
    sub_w = text_size(draw, sub, sub_f)[0]
    panel_w = max(lines_w, sub_w) + 72
    panel_h = 56 + len(big_lines) * 118 + 66
    od.rounded_rectangle([44, 44, 44 + panel_w, 44 + panel_h], radius=26, fill=(10, 24, 42, 178))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(img)
    y = 44 + 40
    for s in big_lines:
        draw.text((44 + 36, y), s, font=big_f, fill=WHITE)
        y += 118
    draw.line([44 + 38, y + 4, 44 + 38 + 64, y + 4], fill=accent, width=7)
    draw.text((44 + 36, y + 18), sub, font=sub_f, fill=(235, 240, 246))
    out = os.path.join(BASE, post_dir, "thumb.png")
    img.convert("RGB").save(out, quality=95)
    print("OK", out)
    return out


def card_canvas(w, h, title, caption=None):
    img = Image.new("RGB", (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w, 108], fill=NAVY)
    draw.text((48, 30), title, font=bold(46), fill=WHITE)
    if caption:
        cw, _ = text_size(draw, caption, reg(28))
        draw.text((w - 48 - cw, h - 58), caption, font=reg(28), fill=GRAY)
    return img, draw


def rows_card(post_dir, fname, title, rows, caption, row_h=88):
    h = 108 + row_h * len(rows) + (64 if caption else 28)
    img, draw = card_canvas(1200, h, title, caption)
    y = 108
    for i, (label, value, vcolor) in enumerate(rows):
        if i % 2 == 0:
            draw.rectangle([0, y, 1200, y + row_h], fill=BG_SOFT)
        draw.text((48, y + row_h // 2 - 24), label, font=reg(38), fill=INK)
        vw, _ = text_size(draw, value, bold(40))
        draw.text((1200 - 48 - vw, y + row_h // 2 - 25), value, font=bold(40), fill=vcolor)
        draw.line([48, y + row_h - 1, 1152, y + row_h - 1], fill=LINE, width=1)
        y += row_h
    out = os.path.join(BASE, post_dir, fname)
    img.save(out, quality=95)
    print("OK", out)
    return out


def steps_card(post_dir, fname, title, steps, caption):
    h = 470
    img, draw = card_canvas(1200, h, title, caption)
    box_w = 336
    gap = (1200 - 96 - box_w * 3) // 2
    y0 = 140
    for i, (label, date, body_lines) in enumerate(steps):
        x = 48 + i * (box_w + gap)
        draw.rounded_rectangle([x, y0, x + box_w, y0 + 240], radius=20, fill=BG_SOFT, outline=NAVY_LIGHT, width=3)
        draw.text((x + 28, y0 + 22), label, font=bold(40), fill=NAVY)
        draw.text((x + 28, y0 + 76), date, font=bold(38), fill=INK)
        yy = y0 + 140
        for ln in body_lines:
            draw.text((x + 28, yy), ln, font=reg(29), fill=GRAY)
            yy += 42
        if i < 2:
            ax = x + box_w + gap // 2
            draw.polygon([(ax - 10, y0 + 104), (ax + 14, y0 + 118), (ax - 10, y0 + 132)], fill=NAVY)
    out = os.path.join(BASE, post_dir, fname)
    img.save(out, quality=95)
    print("OK", out)
    return out


def checklist_card(post_dir, fname, title, items, caption):
    row_h = 96
    h = 108 + row_h * len(items) + 64
    img, draw = card_canvas(1200, h, title, caption)
    y = 108
    for i, (head, desc) in enumerate(items):
        if i % 2 == 0:
            draw.rectangle([0, y, 1200, y + row_h], fill=BG_SOFT)
        draw.ellipse([48, y + 26, 92, y + 70], fill=NAVY)
        draw.text((70, y + 49), str(i + 1), font=bold(30), fill=WHITE, anchor="mm")
        draw.text((116, y + 14), head, font=bold(36), fill=INK)
        draw.text((116, y + 56), desc, font=reg(29), fill=GRAY)
        y += row_h
    out = os.path.join(BASE, post_dir, fname)
    img.save(out, quality=95)
    print("OK", out)
    return out


def flow_card(post_dir, fname, title, steps, caption):
    row_h = 84
    h = 108 + row_h * len(steps) + 64
    img, draw = card_canvas(1200, h, title, caption)
    y = 108
    for i, (label, value) in enumerate(steps):
        last = i == len(steps) - 1
        draw.rounded_rectangle([180, y + 10, 1020, y + row_h - 10], radius=16,
                               fill=(255, 243, 224) if last else BG_SOFT,
                               outline=RED if last else NAVY_LIGHT, width=3 if last else 2)
        tw, _ = text_size(draw, f"{label}  {value}", bold(38) if last else reg(36))
        draw.text(((1200 - tw) / 2, y + row_h // 2 - 24), f"{label}  ", font=reg(36), fill=GRAY)
        draw.text(((1200 - tw) / 2 + text_size(draw, f"{label}  ", reg(36))[0], y + row_h // 2 - 25),
                  value, font=bold(38), fill=RED if last else INK)
        if not last:
            draw.polygon([(592, y + row_h - 8), (608, y + row_h - 8), (600, y + row_h + 4)], fill=NAVY_LIGHT)
        y += row_h
    out = os.path.join(BASE, post_dir, fname)
    img.save(out, quality=95)
    print("OK", out)
    return out


def two_box_card(post_dir, fname, title, boxes, caption):
    h = 470
    img, draw = card_canvas(1200, h, title, caption)
    box_w = 528
    for i, (head, lines) in enumerate(boxes):
        x = 48 + i * (box_w + 48)
        draw.rounded_rectangle([x, 150, x + box_w, 380], radius=20, fill=BG_SOFT, outline=NAVY_LIGHT, width=3)
        draw.text((x + 32, 176), head, font=bold(42), fill=NAVY)
        yy = 244
        for ln in lines:
            draw.text((x + 32, yy), ln, font=reg(32), fill=INK)
            yy += 48
    out = os.path.join(BASE, post_dir, fname)
    img.save(out, quality=95)
    print("OK", out)
    return out


def main():
    # 썸네일 (배경이 있는 4건 — 04 파킹통장은 배경 생성 후 다음 턴)
    make_thumbnail("B2-20261014-01", ["코스피 -5.46%"], "외국인 약 4.5조 원 순매도")
    make_thumbnail("B2-20261014-02", ["1억 증여하면", "세금 485만 원"], "공제 5,000만 원부터 확인")
    make_thumbnail("B2-20261014-03", ["청년미래적금", "10월 16일 마감"], "정부기여금 최대 12% · 월 50만 원")
    make_thumbnail("B2-20261014-05", ["연말정산", "1월에 하면 늦습니다"], "연말 전에 점검할 체크리스트 5가지")

    # 01 코스피 수치 카드
    rows_card("B2-20261014-01", "card-market.png", "숫자로 본 시장 — 13일 급락, 14일 마감", [
        ("코스피 (13일)", "6,035.35 · -5.46%", RED),
        ("삼성전자 (13일)", "-7.39%", RED),
        ("SK하이닉스 (13일)", "-10.09%", RED),
        ("외국인 순매도 (13일)", "약 4조 5,000억 원", INK),
        ("개인 순매수 (13일)", "약 2조 2,300억 원", INK),
        ("코스피 (14일 마감)", "6,008.81 · -0.44%", RED),
    ], "6거래일 연속 하락 · 한국거래소 마감 기준, 복수 매체 교차 확인")

    # 02 증여세 공제 표 + 계산도
    rows_card("B2-20261014-02", "card-deduction.png", "증여재산공제 — 10년 합산 기준", [
        ("배우자", "6억 원", NAVY),
        ("직계존속 → 성년 자녀", "5,000만 원", NAVY),
        ("직계존속 → 미성년 자녀", "2,000만 원", NAVY),
        ("직계비속", "5,000만 원", NAVY),
        ("기타 친족", "1,000만 원", NAVY),
    ], "부모·조부모는 한 그룹으로 합산 · 국세청 기준")
    flow_card("B2-20261014-02", "card-calc.png", "1억 원을 증여하면 세금은?", [
        ("증여액", "1억 원"),
        ("증여재산공제", "- 5,000만 원"),
        ("과세표준", "5,000만 원"),
        ("세율 10%", "산출세액 500만 원"),
        ("신고세액공제 3%", "- 15만 원"),
        ("납부액", "485만 원"),
    ], "성년 자녀에게 증여하는 경우 · 기한 내 신고 기준")

    # 03 청년미래적금 자격 + 일정
    rows_card("B2-20261014-03", "card-eligibility.png", "청년미래적금 2차 — 자격 자가체크", [
        ("연령", "만 19~34세", NAVY),
        ("개인 요건", "총급여 7,500만 원 이하", NAVY),
        ("소상공인", "연매출 3억 원 이하", NAVY),
        ("가구 요건", "중위소득 200% 이하", NAVY),
        ("소득 기준연도", "2025년 확정소득", NAVY),
    ], "가구 150% 조건이 붙는 구간 있음 · 금융위원회 보도자료 기준")
    steps_card("B2-20261014-03", "card-schedule.png", "신청부터 계좌개설까지", [
        ("신청", "~10/16", ["09:00~18:30", "취급기관 앱에서 신청"]),
        ("심사", "10/19~11/13", ["사전 결과 10/30~11/2", "최종 결과 11/12~13"]),
        ("계좌개설", "11/16~27", ["이 기간을 놓치면", "가입 자체가 불가"]),
    ], "선착순 아님 · 카카오뱅크는 별도 한도 있음")

    # 04 파킹통장·ISA 스펙 표 + 자금 도식
    rows_card("B2-20261014-04", "card-isa.png", "ISA 현행 스펙 한눈에", [
        ("납입한도", "연 2,000만 원 · 총 1억 원", NAVY),
        ("비과세", "일반형 200만 원 · 서민형 400만 원", NAVY),
        ("초과분 과세", "9.9% 분리과세 (손익통산)", NAVY),
        ("의무가입", "3년 · 1인 1계좌", NAVY),
        ("서민형 요건", "총급여 5,000만 원 이하 등", NAVY),
    ], "현행 기준 · 한도 확대 등 개편안은 정부안 단계 (미확정)")
    two_box_card("B2-20261014-04", "card-flow.png", "어떤 돈을 어디에 둘까", [
        ("단기 대기 자금 → 파킹통장", ["최고금리보다 적용 한도와", "한도 초과분 금리를 먼저 확인"]),
        ("3년 이상 묶을 돈 → ISA", ["비과세 한도를 활용하고", "개편안은 확정 후 판단"]),
    ], "예금자보호는 금융회사별 1인당 1억 원 (2025년 9월부터)")

    # 05 연말정산 체크리스트
    checklist_card("B2-20261014-05", "card-checklist.png", "연말 전에 점검할 체크리스트 5가지", [
        ("결혼세액공제", "2026년이 마지막 해 — 1인당 50만 원, 생애 1회"),
        ("자녀세액공제", "1명 25만 원 · 2명 55만 원 · 3명부터 추가 30만 원"),
        ("청약저축 공제", "무주택 세대주의 배우자까지 확대 — 연 300만 원 한도 40%"),
        ("카드 전략 · 연금저축", "총급여 25% 초과분부터 공제 · 연말 납입 여력 점검"),
        ("월세 세액공제 증빙", "계약서·이체 내역을 지금 폴더에 모아 두기"),
    ], "제도 항목은 2025년 귀속 기준 · 2026년 귀속은 국세청 안내 후 재확인")


if __name__ == "__main__":
    main()
