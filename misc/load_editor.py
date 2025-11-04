from ursina import *
from ursina.editor.level_editor import LevelEditor

level_editor = LevelEditor()
level_editor.class_menu.available_classes |= {'FirstPersonController':FirstPersonController, 'ThirdPersonController':ThirdPersonController, 'Player':Player, 'Enemy':Enemy} # this is just to add custom classes to the ClassSpawner prefab, you don't really need this
level_editor.goto_scene(0,0)
level_editor.edit_mode = False    # enter play mode