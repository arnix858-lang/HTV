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
cinema_page = r"""import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:http/http.dart' as http;

const String tmdbKey = String.fromEnvironment('TMDB_API_KEY', defaultValue: 'de83af9bf3f4cf2d61cb8a9467045768');
const String posterBase = 'https://image.tmdb.org/t/p/w500';

class CinemaPage extends StatefulWidget {
  const CinemaPage({super.key});
  @override
  State<CinemaPage> createState() => _CinemaPageState();
}

class _CinemaPageState extends State<CinemaPage> {
  final search = TextEditingController();
  List items = [];
  String section = 'Фильмы';
  String heading = 'Популярные фильмы';
  String? error;
  bool loading = false;

  @override
  void initState() { super.initState(); load(); }
  @override
  void dispose() { search.dispose(); super.dispose(); }

  Future<void> load({String? query}) async {
    if (tmdbKey.isEmpty) { setState(() => error = 'Не задан ключ TMDB_API_KEY в GitHub Actions.'); return; }
    setState(() { loading = true; error = null; });
    try {
      String path;
      final params = <String, String>{'api_key': tmdbKey, 'language': 'ru-RU', 'page': '1'};
      if (query != null && query.trim().isNotEmpty) {
        path = '/search/multi'; params['query'] = query.trim(); heading = 'Результаты поиска';
      } else if (section == 'Сериалы') { path = '/tv/popular'; heading = 'Популярные сериалы'; }
      else if (section == 'Мультфильмы') { path = '/discover/movie'; params['with_genres'] = '16'; params['sort_by'] = 'popularity.desc'; heading = 'Мультфильмы'; }
      else if (section == 'Каталог') { path = '/trending/all/week'; heading = 'Популярное сейчас'; }
      else { path = '/movie/popular'; heading = 'Популярные фильмы'; }
      final response = await http.get(Uri.https('api.themoviedb.org', '/3' + path, params)).timeout(const Duration(seconds: 20));
      if (response.statusCode != 200) throw Exception('TMDB HTTP ' + response.statusCode.toString());
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (!mounted) return;
      setState(() { items = (data['results'] as List? ?? []).where((x) => x['media_type'] != 'person').toList(); loading = false; });
    } catch (e) { if (mounted) setState(() { loading = false; error = e.toString(); }); }
  }

  void choose(String value) { setState(() { section = value; search.clear(); }); load(); }

  Widget nav(String label, IconData icon) {
    final active = section == label;
    return Padding(padding: EdgeInsets.symmetric(horizontal: 10.w, vertical: 4.h),
      child: Material(color: active ? Colors.white.withOpacity(.14) : Colors.transparent, borderRadius: BorderRadius.circular(12.r),
        child: InkWell(onTap: () => choose(label), child: Padding(padding: EdgeInsets.all(15.w),
          child: Row(children: [Icon(icon, color: Colors.white), SizedBox(width: 14.w),
            Text(label, style: TextStyle(color: Colors.white, fontSize: 18.sp, fontWeight: active ? FontWeight.bold : FontWeight.normal))]),
        )),
      ));
  }

  void details(Map item) {
    final type = (item['media_type'] ?? (section == 'Сериалы' ? 'tv' : 'movie')).toString();
    Navigator.of(context).push(MaterialPageRoute<void>(
      builder: (_) => CinemaDetailsPage(item: Map<String, dynamic>.from(item), mediaType: type == 'tv' ? 'tv' : 'movie'),
    ));
  }

  @override
  Widget build(BuildContext context) => Scaffold(backgroundColor: const Color(0xFF10131A),
    body: SafeArea(child: Row(children: [
      Container(width: 230.w, color: const Color(0xFF0B0D12), child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        Padding(padding: EdgeInsets.all(22.w), child: const Row(children: [Icon(Icons.live_tv, color: Colors.white), SizedBox(width: 10), Text('HTV', style: TextStyle(color: Colors.white, fontSize: 26, fontWeight: FontWeight.bold))])),
        Padding(padding: EdgeInsets.all(14.w), child: Text('КИНОТЕАТР', style: TextStyle(color: Colors.white38, fontSize: 13.sp, letterSpacing: 2))),
        nav('Фильмы', Icons.movie_outlined),
        nav('Сериалы', Icons.tv_outlined),
        nav('Мультфильмы', Icons.animation_outlined),
        nav('Каталог', Icons.grid_view),
        nav('Поиск', Icons.search),
        const Spacer(),
        Padding(padding: EdgeInsets.fromLTRB(12.w, 10.h, 12.w, 18.h),
          child: SizedBox(width: double.infinity, height: 54.h,
            child: OutlinedButton.icon(
              onPressed: () => Navigator.pop(context),
              icon: const Icon(Icons.arrow_back_rounded, color: Colors.white, size: 21),
              label: const FittedBox(fit: BoxFit.scaleDown, child: Text('На главную', maxLines: 1, style: TextStyle(color: Colors.white, fontSize: 16))),
              style: OutlinedButton.styleFrom(
                alignment: Alignment.centerLeft,
                padding: EdgeInsets.symmetric(horizontal: 14.w),
                side: const BorderSide(color: Colors.white24),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12.r)),
              ),
            ),
          ),
        ),
      ])),
      Expanded(child: Column(children: [
        Padding(padding: EdgeInsets.all(22.w), child: Row(children: [
          Expanded(child: Text(heading, style: TextStyle(color: Colors.white, fontSize: 27.sp, fontWeight: FontWeight.bold))),
          SizedBox(width: 280.w, child: TextField(controller: search, style: const TextStyle(color: Colors.white),
            onSubmitted: (v) => load(query: v),
            decoration: InputDecoration(hintText: 'Поиск фильмов и сериалов', hintStyle: const TextStyle(color: Colors.white38),
              prefixIcon: const Icon(Icons.search, color: Colors.white70), filled: true, fillColor: const Color(0xFF1B1F29),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none)))),
          IconButton(onPressed: () => load(query: search.text), icon: const Icon(Icons.arrow_forward, color: Colors.white)),
        ])),
        Expanded(child: loading && items.isEmpty ? const Center(child: CircularProgressIndicator(color: Colors.white))
          : error != null ? Center(child: Text(error!, style: const TextStyle(color: Colors.white70)))
          : GridView.builder(padding: EdgeInsets.all(22.w),
            gridDelegate: SliverGridDelegateWithMaxCrossAxisExtent(maxCrossAxisExtent: 185.w, mainAxisExtent: 280.h, crossAxisSpacing: 16.w, mainAxisSpacing: 16.h),
            itemCount: items.length, itemBuilder: (ctx, i) {
              final item = items[i] as Map;
              final poster = item['poster_path'];
              final name = (item['title'] ?? item['name'] ?? 'Без названия').toString();
              return InkWell(onTap: () => details(item), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Expanded(child: ClipRRect(borderRadius: BorderRadius.circular(12.r), child: Container(width: double.infinity, color: const Color(0xFF1B1F29),
                  child: poster == null ? const Icon(Icons.movie_outlined, color: Colors.white38, size: 42) : Image.network('https://image.tmdb.org/t/p/w342' + poster.toString(), fit: BoxFit.cover, cacheWidth: 260, filterQuality: FilterQuality.low, gaplessPlayback: true, errorBuilder: (_, __, ___) => const Center(child: Icon(Icons.broken_image_outlined, color: Colors.white38, size: 38)))))),
                SizedBox(height: 7.h),
                Text(name, maxLines: 2, overflow: TextOverflow.ellipsis, style: TextStyle(color: Colors.white, fontSize: 15.sp)),
                Text('★ ' + (item['vote_average'] ?? 0).toString(), style: TextStyle(color: Colors.white60, fontSize: 13.sp)),
              ]));
            })),
      ])),
    ])));
}

class CinemaDetailsPage extends StatefulWidget {
  final Map<String, dynamic> item;
  final String mediaType;
  const CinemaDetailsPage({super.key, required this.item, required this.mediaType});
  @override
  State<CinemaDetailsPage> createState() => _CinemaDetailsPageState();
}

class _CinemaDetailsPageState extends State<CinemaDetailsPage> {
  Map<String, dynamic>? details;
  bool loading = true;
  String? error;

  @override
  void initState() { super.initState(); _loadDetails(); }

  Future<void> _loadDetails() async {
    try {
      final id = widget.item['id'];
      final uri = Uri.https('api.themoviedb.org', '/3/' + widget.mediaType + '/' + id.toString(), {
        'api_key': tmdbKey, 'language': 'ru-RU',
      });
      final response = await http.get(uri).timeout(const Duration(seconds: 18));
      if (response.statusCode != 200) throw Exception('TMDB HTTP ' + response.statusCode.toString());
      if (!mounted) return;
      setState(() { details = jsonDecode(response.body) as Map<String, dynamic>; loading = false; });
    } catch (e) {
      if (!mounted) return;
      setState(() { error = e.toString(); loading = false; });
    }
  }

  String get _date => (details?['release_date'] ?? details?['first_air_date'] ?? widget.item['release_date'] ?? widget.item['first_air_date'] ?? '—').toString();
  String get _title => (details?['title'] ?? details?['name'] ?? widget.item['title'] ?? widget.item['name'] ?? 'Без названия').toString();

  @override
  Widget build(BuildContext context) {
    final backdrop = (details?['backdrop_path'] ?? widget.item['backdrop_path'] ?? '').toString();
    final poster = (details?['poster_path'] ?? widget.item['poster_path'] ?? '').toString();
    final overview = (details?['overview'] ?? widget.item['overview'] ?? 'Описание пока отсутствует.').toString();
    final genres = (details?['genres'] as List? ?? const []);
    final rating = (details?['vote_average'] ?? widget.item['vote_average'] ?? 0).toString();
    final year = _date.length >= 4 ? _date.substring(0, 4) : _date;
    final runtime = details?['runtime'] ?? ((details?['episode_run_time'] is List && (details?['episode_run_time'] as List).isNotEmpty) ? (details?['episode_run_time'] as List).first : null);

    return Scaffold(backgroundColor: const Color(0xFF10131A),
      body: CustomScrollView(slivers: [
        SliverAppBar(pinned: true, backgroundColor: const Color(0xFF10131A), expandedHeight: 330,
          leading: IconButton(icon: const Icon(Icons.arrow_back_rounded, color: Colors.white), onPressed: () => Navigator.pop(context)),
          flexibleSpace: FlexibleSpaceBar(background: Stack(fit: StackFit.expand, children: [
            if (backdrop.isNotEmpty) Image.network('https://image.tmdb.org/t/p/w1280' + backdrop,
              fit: BoxFit.cover, cacheWidth: 1280, filterQuality: FilterQuality.medium,
              errorBuilder: (_, __, ___) => const SizedBox.shrink()),
            const DecoratedBox(decoration: BoxDecoration(gradient: LinearGradient(
              begin: Alignment.topCenter, end: Alignment.bottomCenter,
              colors: [Color(0x22000000), Color(0xFF10131A)], stops: [0.15, 1.0]))),
            Align(alignment: Alignment.bottomLeft, child: Padding(padding: const EdgeInsets.fromLTRB(28, 0, 28, 24),
              child: Text(_title, maxLines: 2, overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: Colors.white, fontSize: 30, fontWeight: FontWeight.w800)))),
          ]))),
        SliverToBoxAdapter(child: Padding(padding: EdgeInsets.fromLTRB(28.w, 8.h, 28.w, 34.h),
          child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            if (poster.isNotEmpty) ClipRRect(borderRadius: BorderRadius.circular(14.r),
              child: Image.network('https://image.tmdb.org/t/p/w342' + poster,
                width: 180.w, height: 270.h, fit: BoxFit.cover, cacheWidth: 360,
                filterQuality: FilterQuality.medium,
                errorBuilder: (_, __, ___) => Container(width: 180.w, height: 270.h,
                  color: const Color(0xFF1B1F29), child: const Icon(Icons.movie_outlined, color: Colors.white54, size: 48)))),
            SizedBox(width: 26.w),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(_title, style: TextStyle(color: Colors.white, fontSize: 28.sp, fontWeight: FontWeight.w800)),
              SizedBox(height: 12.h),
              Wrap(spacing: 9.w, runSpacing: 8.h, children: [
                _chip(year, Icons.calendar_today_outlined), _chip('★ ' + rating, Icons.star_outline_rounded),
                if (runtime != null) _chip(runtime.toString() + ' мин.', Icons.schedule_rounded),
                if (details?['number_of_seasons'] != null) _chip(details!['number_of_seasons'].toString() + ' сез.', Icons.tv_outlined),
              ]),
              SizedBox(height: 18.h),
              if (genres.isNotEmpty) Wrap(spacing: 8.w, runSpacing: 8.h,
                children: genres.map((g) => _chip((g['name'] ?? '').toString(), Icons.local_offer_outlined)).toList()),
              SizedBox(height: 20.h),
              Text('О фильме', style: TextStyle(color: Colors.white, fontSize: 21.sp, fontWeight: FontWeight.bold)),
              SizedBox(height: 8.h),
              Text(overview, style: TextStyle(color: Colors.white70, fontSize: 17.sp, height: 1.5)),
              if (loading) const Padding(padding: EdgeInsets.only(top: 16),
                child: LinearProgressIndicator(color: Colors.white24, backgroundColor: Colors.white10)),
              if (error != null) Padding(padding: const EdgeInsets.only(top: 12),
                child: Text('Не удалось загрузить дополнительные данные: ' + error!, style: const TextStyle(color: Colors.white54))),
            ])),
          ]))),
      ]));
  }

  Widget _chip(String text, IconData icon) => Container(
    padding: EdgeInsets.symmetric(horizontal: 11.w, vertical: 8.h),
    decoration: BoxDecoration(color: Colors.white.withOpacity(.09), borderRadius: BorderRadius.circular(20.r)),
    child: Row(mainAxisSize: MainAxisSize.min, children: [
      Icon(icon, color: Colors.white70, size: 15.sp), SizedBox(width: 6.w),
      Text(text, style: TextStyle(color: Colors.white, fontSize: 14.sp)),
    ]),
  );
}
"""

home_page = r"""import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:video_player_example/pages/iptv/view.dart';
import 'package:video_player_example/pages/settings/view.dart';
import 'package:video_player_example/pages/cinema/view.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});
  void open(BuildContext context, Widget page) => Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => page));

  Widget card(IconData icon, String title, String subtitle, VoidCallback tap) => Expanded(
    child: Padding(padding: EdgeInsets.symmetric(horizontal: 10.w),
      child: Material(color: const Color(0xFF1B1F29), borderRadius: BorderRadius.circular(24.r), clipBehavior: Clip.antiAlias,
        child: InkWell(onTap: tap, child: Container(height: 280.h, padding: EdgeInsets.all(20.w),
          decoration: BoxDecoration(border: Border.all(color: Colors.white12), borderRadius: BorderRadius.circular(24.r)),
          child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
            Container(width: 92.w, height: 92.w, decoration: BoxDecoration(color: Colors.white12, borderRadius: BorderRadius.circular(24.r)),
              child: Icon(icon, color: Colors.white, size: 48.sp)),
            SizedBox(height: 22.h),
            Text(title, textAlign: TextAlign.center, style: TextStyle(color: Colors.white, fontSize: 30.sp, fontWeight: FontWeight.bold)),
            SizedBox(height: 8.h),
            Text(subtitle, textAlign: TextAlign.center, style: TextStyle(color: Colors.white54, fontSize: 18.sp)),
          ]),
        )),
      )),
  );

  @override
  Widget build(BuildContext context) => Scaffold(backgroundColor: const Color(0xFF10131A),
    body: SafeArea(child: Padding(padding: EdgeInsets.all(30.w), child: Column(children: [
      Row(children: [const Icon(Icons.live_tv, color: Colors.white, size: 34), SizedBox(width: 12.w),
        Text('HTV', style: TextStyle(color: Colors.white, fontSize: 34.sp, fontWeight: FontWeight.w800, letterSpacing: 2))]),
      const Spacer(),
      Text('Выберите раздел', style: TextStyle(color: Colors.white, fontSize: 34.sp, fontWeight: FontWeight.bold)),
      SizedBox(height: 30.h),
      SizedBox(height: 280.h, child: Row(children: [
        card(Icons.live_tv, 'ТВ', 'Телеканалы и прямой эфир', () => open(context, const IptvPage())),
        card(Icons.local_movies, 'Кинотеатр', 'Фильмы, сериалы и мультфильмы', () => open(context, const CinemaPage())),
        card(Icons.settings, 'Настройки', 'Настройка приложения и источников', () => open(context, const SettingsPage())),
      ])),
      const Spacer(),
      Text('HTV • Бесплатное приложение', style: TextStyle(color: Colors.white30, fontSize: 16.sp)),
    ]))));
}
"""
cinema_dir = Path("lib/pages/cinema")
cinema_dir.mkdir(parents=True, exist_ok=True)
(cinema_dir / "view.dart").write_text(cinema_page)

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
