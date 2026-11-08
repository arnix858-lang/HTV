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
            children: [
              Icon(_settingIcon(item.title), size: 28.sp, color: textColor),
              SizedBox(width: 12.w),
              Expanded(
                flex: 5,
                child: _SettingMarqueeText(
                  text: item.title,
                  style: AppTheme.text(textColor, 28.sp),
                  height: 38.sp,
                ),
              ),
              SizedBox(width: 10.w),
              Expanded(
                flex: 4,
                child: _SettingMarqueeText(
                  text: item.value(),
                  style: AppTheme.text(textColor, 26.sp),
                  height: 38.sp,
                ),
              ),
            ],
          ),"""
if old not in s: raise SystemExit("Settings header row pattern missing")
s=s.replace(old,new,1)
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
