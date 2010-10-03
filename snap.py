import piggyphoto

C = piggyphoto.camera()

print C.abilities
C.capture_preview('preview.jpg')
C.capture_image('snap.jpg')
