import os
import random
import sys
import pygame as pg
import time

WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：効果トンRect or 爆弾Rect
    戻り値：判定結果タプル（後方向判定結果、 縦方向判定結果）
    True：画面内/False：画面外
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate        

def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を5秒間表示する
    """
    black = pg.Surface((WIDTH, HEIGHT))
    black.fill((0, 0, 0))
    black.set_alpha(200)

    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect(center=(WIDTH//2, HEIGHT//2 + 10))

    cry_img = pg.transform.rotozoom(
        pg.image.load("fig/8.png"), 0, 1.0
    )
    
    left_rct = cry_img.get_rect(
        center = (WIDTH//2 - 200, HEIGHT//2)
    )

    right_rct = cry_img.get_rect(
        center = (WIDTH//2 + 200, HEIGHT//2)
    )

    black.blit(txt, txt_rct)
    black.blit(cry_img, left_rct)
    black.blit(cry_img, right_rct)

    screen.blit(black, (0, 0))
    pg.display.update()

    time.sleep(5)

# ★【追記】10段階の爆弾画像と加速度のリストを生成する関数
def init_bb() -> tuple[list[pg.Surface], list[int]]:
    """
    10段階の大きさを変えた爆弾Surfaceのリストと加速度のリストを準備する
    戻り値：(爆弾Surfaceのリスト, 加速度のリスト)
    """
    bb_imgs = []
    # 1から10までの10段階のサイズを作る
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0)) # 黒を透過
        bb_imgs.append(bb_img)
        
    bb_accs = [a for a in range(1, 11)] # 加速度リスト [1, 2, ..., 10]
    
    return bb_imgs, bb_accs

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    # ★【変更】初期化関数を呼び出してリストを取得する
    bb_imgs, bb_accs = init_bb()
    
    # 最初の設定用（インデックス0番 = 初期段階）
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect() 
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        # ★【追記】時間（tmr）に応じて爆弾の段階（0～9）を決定する
        # 500フレーム（約10秒）ごとに1段階上がります
        idx = min(tmr // 500, 9)
        
        # 加速させた速度（avx, avy）を計算
        # 元の向き（vx, vyがプラスかマイナスか）を保ったまま、リストの倍率を掛け算する
        # ※そのまま vx *= bb_accs[...] とすると毎フレーム無限に乗算されてしまうため、
        # 向きを判定して正しい符号で計算します
        avx = (+5 if vx > 0 else -5) * bb_accs[idx]
        avy = (+5 if vy > 0 else -5) * bb_accs[idx]

        # ★【追記】爆弾SurfaceとRectのサイズを現在の段階に更新
        bb_img = bb_imgs[idx]
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height

        # ★【変更】計算した avx, avy で移動させる
        bb_rct.move_ip(avx, avy)
        
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
            
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
