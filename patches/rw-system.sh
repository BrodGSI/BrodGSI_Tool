#!/system/bin/sh

# Монтирование и исправление базовых симлинков VNDK
mount -o remount,rw / || true

# Исправление подсветки и аудио на Xiaomi/Samsung вендорах
if [ -f /vendor/build.prop ]; then
    VNDK_VER=$(grep "ro.vndk.version=" /vendor/build.prop | cut -d'=' -f2)
    if [ -n "$VNDK_VER" ]; then
        setprop ro.vndk.version "$VNDK_VER"
    fi
fi

# Отключение принудительного шифрования в runtime
setprop vold.decrypt trigger_restart_framework
exit 0