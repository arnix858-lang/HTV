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

# The workflow translates the Chinese group label before this script runs.
# Match the translated group name, not the original upstream label.
more_anchor = "SettingGroup(name: 'Дополнительно', items: ["
more_insert = """SettingGroup(name: 'Дополнительно', items: [
        SettingItem(
          title: 'О приложении',
          value: () => 'Бесплатно',
          description: () => 'Назначение приложения и текущая версия',
          onTap: () => _showAboutApp(),
        ),"""
if more_anchor not in s:
    raise SystemExit("About settings group insertion point missing (translated group)")
if "title: 'О приложении'" not in s:
    s=s.replace(more_anchor, more_insert, 1)

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
    if (title.contains('О приложении')) return FontAwesomeIcons.circleInfo;
    return FontAwesomeIcons.sliders;
  }

"""
if "_settingIcon(String title)" not in s:
    if anchor not in s: raise SystemExit("Setting item method insertion point missing")
    s=s.replace(anchor,icons+anchor,1)
p.write_text(s)
print("Marquee text and Font Awesome setting icons applied.")


# Replace the direct player launch with a three-section home screen.
home_page = r"""import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:video_player_example/pages/iptv/view.dart';
import 'package:video_player_example/pages/settings/view.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  void _openPage(BuildContext context, Widget page) {
    Navigator.of(context).push(
      MaterialPageRoute<void>(builder: (_) => page),
    );
  }

  void _showComingSoon(BuildContext context) {
    showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        backgroundColor: const Color(0xFF20232B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(22)),
        title: const Text('Кинотеатр', style: TextStyle(color: Colors.white)),
        content: const Text(
          'Раздел находится в разработке.\n\nСкоро здесь появятся фильмы, сериалы, мультфильмы и другой контент.',
          style: TextStyle(color: Colors.white70, height: 1.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: const Text('Понятно'),
          ),
        ],
      ),
    );
  }

  Widget _menuCard({
    required BuildContext context,
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
    required Color accent,
  }) {
    return Expanded(
      child: Padding(
        padding: EdgeInsets.symmetric(horizontal: 10.w),
        child: Material(
          color: const Color(0xFF1B1F29),
          borderRadius: BorderRadius.circular(24.r),
          clipBehavior: Clip.antiAlias,
          child: InkWell(
            onTap: onTap,
            borderRadius: BorderRadius.circular(24.r),
            child: Container(
              constraints: BoxConstraints(minHeight: 250.h),
              padding: EdgeInsets.symmetric(horizontal: 18.w, vertical: 24.h),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.white.withOpacity(0.07)),
                borderRadius: BorderRadius.circular(24.r),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    width: 92.w,
                    height: 92.w,
                    decoration: BoxDecoration(
                      color: accent.withOpacity(0.14),
                      borderRadius: BorderRadius.circular(25.r),
                    ),
                    child: Icon(icon, color: accent, size: 48.sp),
                  ),
                  SizedBox(height: 22.h),
                  Text(
                    title,
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.white, fontSize: 30.sp, fontWeight: FontWeight.w700),
                  ),
                  SizedBox(height: 8.h),
                  Text(
                    subtitle,
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(color: Colors.white54, fontSize: 18.sp),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF10131A),
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            return Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: 1450.w),
                child: Padding(
                  padding: EdgeInsets.symmetric(horizontal: 34.w, vertical: 22.h),
                  child: Column(
                    children: [
                      SizedBox(height: 12.h),
                      Row(
                        children: [
                          Icon(Icons.live_tv_rounded, color: const Color(0xFFFF6B35), size: 34.sp),
                          SizedBox(width: 12.w),
                          Text(
                            'HTV',
                            style: TextStyle(color: Colors.white, fontSize: 34.sp, fontWeight: FontWeight.w800, letterSpacing: 2),
                          ),
                        ],
                      ),
                      const Spacer(),
                      Text(
                        'Выберите раздел',
                        style: TextStyle(color: Colors.white, fontSize: 34.sp, fontWeight: FontWeight.w700),
                      ),
                      SizedBox(height: 30.h),
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          _menuCard(
                            context: context,
                            icon: Icons.live_tv_rounded,
                            title: 'ТВ',
                            subtitle: 'Телеканалы и прямой эфир',
                            accent: const Color(0xFFFF7043),
                            onTap: () => _openPage(context, const IptvPage()),
                          ),
                          _menuCard(
                            context: context,
                            icon: Icons.local_movies_rounded,
                            title: 'Кинотеатр',
                            subtitle: 'Фильмы, сериалы и мультфильмы',
                            accent: const Color(0xFF8B7CFF),
                            onTap: () => _showComingSoon(context),
                          ),
                          _menuCard(
                            context: context,
                            icon: Icons.settings_rounded,
                            title: 'Настройки',
                            subtitle: 'Настройка приложения и источников',
                            accent: const Color(0xFF55B8E8),
                            onTap: () => _openPage(context, const SettingsPage()),
                          ),
                        ],
                      ),
                      const Spacer(),
                      Text(
                        'HTV • Бесплатное приложение',
                        style: TextStyle(color: Colors.white30, fontSize: 16.sp),
                      ),
                      SizedBox(height: 10.h),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
"""
home_dir = Path("lib/pages/home")
home_dir.mkdir(parents=True, exist_ok=True)
(home_dir / "view.dart").write_text(home_page)

main = Path("lib/main.dart")
main_text = main.read_text()
home_import = "import 'package:video_player_example/pages/home/view.dart';"
if home_import not in main_text:
    main_text = main_text.replace(
        "import 'package:video_player_example/pages/index.dart';",
        "import 'package:video_player_example/pages/index.dart';\n" + home_import,
        1,
    )
old_home = """home: const DelayRenderer(
              child: DoubleBackExit(
                child: IptvPage(),
              ),
            ),"""
new_home = """home: const DelayRenderer(
              child: DoubleBackExit(
                child: HomePage(),
              ),
            ),"""
if old_home in main_text:
    main_text = main_text.replace(old_home, new_home, 1)
elif "child: HomePage()," not in main_text:
    raise SystemExit("Could not locate initial IPTV home widget in main.dart")
main.write_text(main_text)
print("Three-button HTV home screen installed.")
