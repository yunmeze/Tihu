# Stable user-data location

The project fixes Godot's application/config/use_custom_user_dir=true and application/config/custom_user_dir_name=Tihu-Legend-Godot. This prevents later changes to the displayed project name from selecting a different user:// directory. Both settings were checked as supported by installed Godot4.6.3.

The actual platform path comes from OS.get_user_data_dir(); do not hardcode a Linux or Windows absolute path. Linux was verified under an isolated XDG_DATA_HOME. Windows path/runtime testing remains pending. No old directory is read or migrated by this settings change. At this checkpoint the game has no integrated player-save feature; isolated test data is not recovered player progress.

Future inventory or complete-game stores must use their own explicitly created dedicated subdirectory and schema. Keeping the user directory stable is not a backup, filesystem durability guarantee, or permission to overwrite an incompatible save.
