from ursina import *
from ursina.editor.level_editor import LevelEditor

app = Ursina()

level_editor = LevelEditor()
level_editor.goto_scene(0,0)

app.run()