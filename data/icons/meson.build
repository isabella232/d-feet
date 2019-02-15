# FIXME: the 16x16 seem all wrong. Hicolor is for public app icons,
# not private icons and these are all off-style and should be
# scalable symbolics.

icon16_data = files(
  'hicolor/16x16/apps/dfeet-method-category.png',
  'hicolor/16x16/apps/dfeet-method.png',
  'hicolor/16x16/apps/dfeet-object.png',
  'hicolor/16x16/apps/dfeet-property-category.png',
  'hicolor/16x16/apps/dfeet-property.png',
  'hicolor/16x16/apps/dfeet-signal-category.png',
  'hicolor/16x16/apps/dfeet-signal.png',
  'hicolor/16x16/apps/dfeet-icon-default-service.png',
)

icons = {
  '16x16': icon16_data,
  'scalable': 'hicolor/scalable/apps/org.gnome.dfeet.svg',
  'symbolic': 'hicolor/symbolic/apps/org.gnome.dfeet-symbolic.svg'
}

foreach size, data: icons
  install_data(
    data,
    install_dir: df_datadir / 'icons/hicolor' / size / 'apps',
  )
endforeach
