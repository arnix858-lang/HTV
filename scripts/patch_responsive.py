from pathlib import Path

def patch(path, old, new, label):
    p=Path(path); s=p.read_text()
    if old not in s: raise SystemExit("Pattern missing: "+label)
    p.write_text(s.replace(old,new,1))

# Long setting labels/values scroll horizontally only when they do not fit.
p=Path("pubspec.yaml")
s=p.read_text()
if "  marquee:" not in s:
    s=s.replace("  pretty_qr_code: ^3.3.0", "  pretty_qr_code: ^3.3.0\n  marquee: ^2.3.0\n  font_awesome_flutter: 10.7.0")
p.write_text(s)

p=Path("lib/pages/settings/widgets/settings.dart")
s=p.read_text()
if "package:marquee/marquee.dart" not in s:
    s=s.replace("import 'package:flutter/material.dart';", "import 'package:flutter/material.dart';\nimport 'package:marquee/marquee.dart';\nimport 'package:font_awesome_flutter/font_awesome_flutter.dart';")
if "package_info_plus/package_info_plus.dart" not in s:
    s=s.replace("import 'package:flutter/material.dart';", "import 'package:flutter/material.dart';\nimport 'package:package_info_plus/package_info_plus.dart';")
# Add a reusable overflow-aware marquee widget before SettingsMain.
anchor="class SettingsMain extends StatefulWidget {"
widget="""class _SettingMarqueeText extends StatelessWidget {
  final String text;
  final TextStyle style;
  final double height;

  const _SettingMarqueeText({
    required this.text,
    required this.style,
    this.height = 42,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final painter = TextPainter(
          text: TextSpan(text: text, style: style),
          textDirection: Directionality.of(context),
          maxLines: 1,
        )..layout(maxWidth: double.infinity);
        if (painter.width <= constraints.maxWidth) {
          return SizedBox(
            height: height,
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text(text, style: style, maxLines: 1, overflow: TextOverflow.ellipsis),
            ),
          );
        }
        return SizedBox(
          height: height,
          child: Marquee(
            text: text,
            style: style,
            blankSpace: 36,
            velocity: 28,
            pauseAfterRound: const Duration(seconds: 1),
            startPadding: 8,
            accelerationDuration: const Duration(milliseconds: 500),
            decelerationDuration: const Duration(milliseconds: 300),
          ),
        );
      },
    );
  }
}

"""
if "_SettingMarqueeText" not in s:
    if anchor not in s: raise SystemExit("SettingsMain insertion point missing")
    s=s.replace(anchor,widget+anchor,1)

old="""          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                item.title,
                style: AppTheme.text(textColor, 30.sp),
              ),
              Text(
                item.value(),
                style: AppTheme.text(textColor, 30.sp),
              ),
            ],
          ),"""
new="""          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Icon(_settingIcon(item.title), size: 38.sp, color: textColor),
              SizedBox(width: 20.w),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    _SettingMarqueeText(
                      text: item.title,
                      style: AppTheme.text(textColor, 28.sp),
                      height: 38.sp,
                    ),
                    SizedBox(height: 5.h),
                    _SettingMarqueeText(
                      text: item.value(),
                      style: AppTheme.text(AppTheme.fgFaded(context, AppTheme.oSecondary), 22.sp),
                      height: 30.sp,
                    ),
                  ],
                ),
              ),
            ],
          ),"""
if old not in s: raise SystemExit("Settings header row pattern missing")
s=s.replace(old,new,1)
# Add a localized About dialog with the actual installed app version.
about_method = """  Future<void> _showAboutApp() async {
    final info = await PackageInfo.fromPlatform();
    if (!mounted) return;
    showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('О приложении'),
        content: SingleChildScrollView(
          child: Text(
            'HTV — приложение для просмотра телеканалов, фильмов, сериалов, мультфильмов и другого видеоконтента.\\n\\n'
            'Приложение предоставляется абсолютно бесплатно. Оплата и подписка не требуются.\\n\\n'
            'Версия: ${info.version} (${info.buildNumber})',
            style: AppTheme.text(AppTheme.fg(context), 18.sp),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: const Text('Закрыть'),
          ),
        ],
      ),
    );
  }

"""
method_anchor = "  void _showServerQrcode() {"
if method_anchor not in s:
    raise SystemExit("About dialog insertion point missing")
s = s.replace(method_anchor, about_method + method_anchor, 1)

more_old = """      SettingGroup(name: '更多', items: [
        SettingItem(
          title: '更多设置',"""
more_new = """      SettingGroup(name: '更多', items: [
        SettingItem(
          title: 'О приложении',
          value: () => 'Бесплатно',
          description: () => 'Назначение приложения и текущая версия',
          onTap: () => _showAboutApp(),
        ),
        SettingItem(
          title: '更多设置',"""
if more_old not in s:
    raise SystemExit("About setting item insertion point missing")
s = s.replace(more_old, more_new, 1)

p.write_text(s)

# Insert icon mapping before _buildSettingItem.
anchor="  Widget _buildSettingItem(SettingItem item, bool isSelected) {"
icons="""  IconData _settingIcon(String title) {
    if (title.contains('Автозапуск')) return FontAwesomeIcons.powerOff;
    if (title.contains('канал') || title.contains('каналов')) return FontAwesomeIcons.tv;
    if (title.contains('источник') || title.contains('плейлист')) return FontAwesomeIcons.list;
    if (title.contains('программа') || title.contains('телепрограмма')) return FontAwesomeIcons.calendarDays;
    if (title.contains('кэш')) return FontAwesomeIcons.database;
    if (title.contains('параметр') || title.contains('пользовател')) return FontAwesomeIcons.userGear;
    if (title.contains('обратное') || title.contains('переключение')) return FontAwesomeIcons.repeat;
    if (title.contains('обновлен')) return FontAwesomeIcons.arrowsRotate;
    if (title.contains('сообщество') || title.contains('обратная связь')) return FontAwesomeIcons.comments;
    return FontAwesomeIcons.sliders;
  }

"""
if "_settingIcon(String title)" not in s:
    if anchor not in s: raise SystemExit("Setting item method insertion point missing")
    s=s.replace(anchor,icons+anchor,1)
p.write_text(s)
print("Marquee text and Font Awesome setting icons applied.")
