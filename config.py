debug = False

filetypes = [('Kõik pildifailid', '.gif .jpg .png'), ('GIF fail', '*.gif'), ('JPEG fail', '*.jpg'), ('PNG fail', '*.png')]
window_paddings = (70, 70) # Akna minimaalne kaugus ekraani servadest (hor, vert)
thumbnail_size = (100, 100) # Efekti eelvaate pisipildi maksimaalne suurus (x, y)
preview_size = (None, None) # Väärtustatakse Tk() väljakutsel

# Kuna mahukate piltide töötlemine on aeganõudev, siis järgmiste parameetrite abil saab muuta seda,
#   kuidas erinevad pildid liidesel (suur eelvaade ja efektide eelvaated) genereeritakse. Väärtus "original" laeb kõige kauem,
#   aga näitab kõige täpsemat tulemust (ehk seda milline pilt välja näeks kui see salvestada).

preview_basis = "preview" # original või preview
thumbnail_basis = "preview" # original, preview või thumbnail