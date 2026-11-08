from pathlib import Path

def patch(path, old, new, label):
    p=Path(path); s=p.read_text()
    if old not in s: raise SystemExit("Pattern missing: "+label)
    p.write_text(s.replace(old,new,1))

# Long setting labels/values scroll horizontally only when they do not fit.
p=Path("pubspec.yaml")
s=p.read_text()
if "  marquee:" not in s:
    s=s.replace("  pretty_qr_code: ^3.3.0", "  pretty_qr_code: ^3.3.0\n  marquee: ^2.3.0\n  font_awesome_flutter: 10.7.0\n  video_player: ^2.9.2")
if "  webview_flutter:" not in s:
    s=s.replace("  pretty_qr_code: ^3.3.0", "  pretty_qr_code: ^3.3.0\n  webview_flutter: ^4.8.0")
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
import 'dart:ui' show ImageFilter;
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'package:video_player/video_player.dart';

const String tmdbKey = String.fromEnvironment('TMDB_API_KEY', defaultValue: 'de83af9bf3f4cf2d61cb8a9467045768');
const String tmdbProxyBase = String.fromEnvironment('TMDB_PROXY_URL', defaultValue: '');
Uri tmdbApiUri(String path, Map<String, String> params) {
  final proxy = tmdbProxyBase.trim().replaceAll(RegExp(r'/+

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
  List<String> favoriteIds = [];

  @override
  void initState() { super.initState(); _loadFavorites(); load(); }

  Future<void> _loadFavorites() async {
    final prefs = await SharedPreferences.getInstance();
    if (mounted) setState(() => favoriteIds = prefs.getStringList('cinema_favorites') ?? []);
  }
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
      final cacheKey = 'tmdb_catalog_' + path + '_' + (params['query'] ?? '') + '_' + (params['with_genres'] ?? '');
      final prefs = await SharedPreferences.getInstance();
      final cached = prefs.getString(cacheKey);
      if (cached != null && mounted) {
        final cachedData = jsonDecode(cached) as Map<String, dynamic>;
        setState(() { items = (cachedData['results'] as List? ?? []).where((x) => x['media_type'] != 'person').toList(); loading = false; });
      }
      final response = await http.get(tmdbApiUri('/3' + path, params)).timeout(const Duration(seconds: 15));
      if (response.statusCode != 200) throw Exception('TMDB HTTP ' + response.statusCode.toString());
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      await prefs.setString(cacheKey, response.body);
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
                  child: poster == null ? const Icon(Icons.movie_outlined, color: Colors.white38, size: 42) : Image.network(tmdbImageUrl('/t/p/w342' + poster.toString()), fit: BoxFit.cover, cacheWidth: 260, filterQuality: FilterQuality.low, gaplessPlayback: true, errorBuilder: (_, __, ___) => const Center(child: Icon(Icons.broken_image_outlined, color: Colors.white38, size: 38)))))),
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
  bool isFavorite = false;

  @override
  void initState() { super.initState(); _loadDetails(); _loadFavorite(); }

  String get _favoriteKey => widget.mediaType + '_' + widget.item['id'].toString();

  Future<void> _loadFavorite() async {
    final prefs = await SharedPreferences.getInstance();
    if (mounted) setState(() => isFavorite = (prefs.getStringList('cinema_favorites') ?? []).contains(_favoriteKey));
  }

  Future<void> _toggleFavorite() async {
    final prefs = await SharedPreferences.getInstance();
    final ids = prefs.getStringList('cinema_favorites') ?? [];
    if (ids.contains(_favoriteKey)) { ids.remove(_favoriteKey); } else { ids.add(_favoriteKey); }
    await prefs.setStringList('cinema_favorites', ids);
    if (mounted) setState(() => isFavorite = ids.contains(_favoriteKey));
  }

  void _watch() {
    Navigator.of(context).push(MaterialPageRoute<void>(
      builder: (_) => VideoSourcesPage(
        title: _title,
        originalTitle: (details?['original_title'] ?? details?['original_name'] ?? widget.item['original_title'] ?? widget.item['original_name'] ?? _title).toString(),
        year: _date.length >= 4 ? _date.substring(0, 4) : '',
        mediaType: widget.mediaType,
      ),
    ));
  }

  Future<void> _loadDetails() async {
    try {
      final id = widget.item['id'];
      final uri = tmdbApiUri('/3/' + widget.mediaType + '/' + id.toString(), {
        'api_key': tmdbKey, 'language': 'ru-RU', 'append_to_response': 'credits',
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
    final tagline = (details?['tagline'] ?? '').toString();
    final status = (details?['status'] ?? '').toString();
    final countryList = (details?['production_countries'] as List? ?? const []).map((x) => (x['name'] ?? '').toString()).where((x) => x.isNotEmpty).take(2).join(', ');
    final cast = (details?['credits']?['cast'] as List? ?? const []).take(3).map((x) => (x['name'] ?? '').toString()).where((x) => x.isNotEmpty).join(' • ');
    final screenWidth = MediaQuery.of(context).size.width;
    final isTv = screenWidth >= 900;
    final compact = screenWidth < 600;

    final favoriteButton = OutlinedButton.icon(
      autofocus: isTv,
      onPressed: _toggleFavorite,
      icon: Icon(isFavorite ? Icons.favorite : Icons.favorite_border,
        color: isFavorite ? Colors.pinkAccent : Colors.white, size: isTv ? 27 : 21),
      label: Text(isFavorite ? 'В избранном' : 'В избранное',
        style: TextStyle(color: Colors.white, fontSize: isTv ? 20 : 15, fontWeight: FontWeight.w600)),
      style: OutlinedButton.styleFrom(
        minimumSize: Size(isTv ? 250 : 0, isTv ? 64 : 52),
        padding: EdgeInsets.symmetric(horizontal: isTv ? 28 : 16, vertical: isTv ? 18 : 14),
        side: const BorderSide(color: Colors.white70, width: 1.5),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
    final watchButton = FilledButton.icon(
      onPressed: _watch,
      icon: Icon(Icons.play_arrow_rounded, color: Colors.white, size: isTv ? 30 : 22),
      label: Text('Смотреть', style: TextStyle(color: Colors.white,
        fontSize: isTv ? 21 : 16, fontWeight: FontWeight.bold)),
      style: FilledButton.styleFrom(
        minimumSize: Size(isTv ? 230 : 0, isTv ? 64 : 52),
        padding: EdgeInsets.symmetric(horizontal: isTv ? 32 : 18, vertical: isTv ? 18 : 14),
        backgroundColor: const Color(0xFFE65A32),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );

    return Scaffold(
      backgroundColor: const Color(0xFF080A0F),
      body: Stack(fit: StackFit.expand, children: [
        if (backdrop.isNotEmpty)
          ImageFiltered(
            imageFilter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
            child: Image.network(
              tmdbImageUrl('/t/p/w1280' + backdrop),
              fit: BoxFit.cover,
              cacheWidth: 1600,
              gaplessPlayback: true,
              errorBuilder: (_, __, ___) => const SizedBox.shrink(),
            ),
          ),
        const DecoratedBox(decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0x99060910), Color(0xE6080A0F), Color(0xFF080A0F)],
            stops: [0.0, 0.48, 1.0],
          ),
        )),
        SafeArea(child: Column(children: [
          SizedBox(
            height: 54,
            child: Row(children: [
              IconButton(
                icon: const Icon(Icons.arrow_back_rounded, color: Colors.white, size: 28),
                onPressed: () => Navigator.pop(context),
              ),
              const SizedBox(width: 8),
              Expanded(child: Text(
                _title,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w700),
              )),
              const SizedBox(width: 16),
            ]),
          ),
          Expanded(child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: EdgeInsets.fromLTRB(compact ? 16 : 42, 12, compact ? 16 : 42, 34),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              LayoutBuilder(builder: (context, constraints) {
                final posterWidth = (constraints.maxWidth * (compact ? 0.38 : isTv ? 0.25 : 0.23)).clamp(112.0, isTv ? 340.0 : 260.0);
                final posterHeight = posterWidth * 1.48;
                return Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  if (poster.isNotEmpty)
                    ClipRRect(borderRadius: BorderRadius.circular(12), child: Image.network(
                      tmdbImageUrl('/t/p/w500' + poster), width: posterWidth, height: posterHeight,
                      fit: BoxFit.cover, cacheWidth: 520, filterQuality: FilterQuality.medium, gaplessPlayback: true,
                      errorBuilder: (_, __, ___) => Container(width: posterWidth, height: posterHeight, color: const Color(0xFF1B1F29), child: const Icon(Icons.movie_outlined, color: Colors.white54, size: 42)),
                    )),
                  SizedBox(width: compact ? 16 : 34),
                  Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text(_title, maxLines: 3, overflow: TextOverflow.ellipsis, style: TextStyle(color: Colors.white, fontSize: compact ? 22 : 34, fontWeight: FontWeight.w800, height: 1.12)),
                    if (tagline.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 7), child: Text(tagline, style: const TextStyle(color: Colors.white60, fontStyle: FontStyle.italic))),
                    SizedBox(height: 12),
                    Wrap(spacing: 8, runSpacing: 8, children: [
                      _chip(year, Icons.calendar_today_outlined), _chip('★ ' + rating, Icons.star_outline_rounded),
                      if (runtime != null) _chip(runtime.toString() + ' мин.', Icons.schedule_rounded),
                      if (details?['number_of_seasons'] != null) _chip(details!['number_of_seasons'].toString() + ' сез.', Icons.tv_outlined),
                      if (details?['number_of_episodes'] != null) _chip(details!['number_of_episodes'].toString() + ' сер.', Icons.video_library_outlined),
                      if (status.isNotEmpty) _chip(status, Icons.info_outline),
                    ]),
                    if (genres.isNotEmpty) ...[SizedBox(height: 12), Wrap(spacing: 7, runSpacing: 7, children: genres.take(compact ? 4 : 7).map((g) => _chip((g['name'] ?? '').toString(), Icons.local_offer_outlined)).toList())],
                  ])),
                ]);
              }),
              SizedBox(height: 22),
              Wrap(spacing: 12, runSpacing: 10, children: [
                watchButton,
                favoriteButton,
              ]),
              SizedBox(height: 24),
              Text('О фильме', style: TextStyle(color: Colors.white, fontSize: compact ? 19 : 24, fontWeight: FontWeight.bold)),
              SizedBox(height: 9),
              Text(overview, style: TextStyle(color: Colors.white.withOpacity(.86), fontSize: compact ? 14 : 17, height: 1.55)),
              if (countryList.isNotEmpty || details?['original_language'] != null) ...[
                SizedBox(height: 18),
                Text([if (countryList.isNotEmpty) countryList, if (details?['original_language'] != null) 'Язык: ' + details!['original_language'].toString().toUpperCase()].join('  •  '), style: const TextStyle(color: Colors.white60, fontSize: 13)),
              ],
              if (cast.isNotEmpty) ...[
                SizedBox(height: 18),
                Text('В ролях', style: TextStyle(color: Colors.white, fontSize: compact ? 18 : 22, fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                Text(cast, style: const TextStyle(color: Colors.white70, fontSize: 14)),
              ],
              if (loading) const Padding(padding: EdgeInsets.only(top: 18), child: LinearProgressIndicator(color: Colors.white38, backgroundColor: Colors.white12)),
              if (error != null) const Padding(padding: EdgeInsets.only(top: 10), child: Text('Не удалось загрузить данные', style: TextStyle(color: Colors.white54))),
            ]),
          )),
        ])),
      ]),
    );
  }

  Widget _chip(String text, IconData icon) => Container(
    padding: EdgeInsets.symmetric(horizontal: 11.w, vertical: 8.h),
    decoration: BoxDecoration(color: Colors.white.withOpacity(.09), borderRadius: BorderRadius.circular(20.r)),
    child: Row(mainAxisSize: MainAxisSize.min, children: [
      Icon(icon, color: Colors.white70, size: 15.sp), SizedBox(width: 6.w),
      Text(text, style: TextStyle(color: Colors.white, fontSize: 13.sp)),
    ]),
  );

}

class VideoSourcesPage extends StatefulWidget {
  final String title, originalTitle, year, mediaType;
  const VideoSourcesPage({super.key, required this.title, required this.originalTitle, required this.year, required this.mediaType});
  @override
  State<VideoSourcesPage> createState() => _VideoSourcesPageState();
}
class _VideoSourcesPageState extends State<VideoSourcesPage> {
  List<Map<String,dynamic>> translations = [];
  bool loading = false;
  String? error;
  static const base = 'https://hdrezka.ag';
  static const ua = 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36';
  @override
  void initState() { super.initState(); _search(); }
  String clean(String s) => s.replaceAll(RegExp(r'<[^>]*>'),' ').replaceAll('&nbsp;',' ').replaceAll('&amp;','&').replaceAll('&quot;','"').replaceAll(RegExp(r'\s+'),' ').trim();
  String norm(String s) => s.toLowerCase().replaceAll(RegExp(r'[^a-zа-яё0-9]'),'');
  Future<void> _search() async {
    setState(() { loading=true; error=null; translations=[]; });
    try {
      final r=await http.get(Uri.parse(base+'/engine/ajax/search.php?q='+Uri.encodeQueryComponent(widget.title)),headers:{'User-Agent':ua,'Accept':'text/html,*/*'}).timeout(const Duration(seconds:20));
      if(r.statusCode!=200) throw Exception('HDRezka HTTP '+r.statusCode.toString());
      final found=<Map<String,dynamic>>[];
      final a=RegExp(r'''<a\b[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)</a>''',caseSensitive:false);
      for(final m in a.allMatches(r.body)) {
        final href=(m.group(1)??'').replaceAll('&amp;','&');
        final name=clean(m.group(2)??'');
        final n=norm(name), t=norm(widget.title), o=norm(widget.originalTitle);
        if(href.isEmpty || name.isEmpty || !(n.contains(t)||t.contains(n)||n.contains(o)||o.contains(n))) continue;
        final url=href.startsWith('http')?href:base+href;
        final page=await http.get(Uri.parse(url),headers:{'User-Agent':ua,'Referer':base+'/'}).timeout(const Duration(seconds:20));
        if(page.statusCode!=200) continue;
        final html=page.body;
        final idMatch=RegExp(r'''id=["']post_id["'][^>]*value=["'](\d+)''',caseSensitive:false).firstMatch(html)
          ?? RegExp(r'''value=["'](\d+)["'][^>]*id=["']post_id["']''',caseSensitive:false).firstMatch(html)
          ?? RegExp(r'''(?:post_id|initCDNSeriesEvents|initCDNMoviesEvents)\s*[:=(]\s*["']?(\d+)''',caseSensitive:false).firstMatch(html);
        if(idMatch==null) continue;
        final trs=RegExp(r'''data-translator_id=["'](\d+)["'][^>]*>([\s\S]*?)</li>''',caseSensitive:false);
        for(final tr in trs.allMatches(html)) {
          final tid=tr.group(1)??'', label=clean(tr.group(2)??'');
          if(tid.isEmpty || found.any((x)=>x['translatorId']==tid && x['id']==idMatch.group(1))) continue;
          found.add({'id':idMatch.group(1),'translatorId':tid,'name':label.isEmpty?'Озвучка '+tid:label,'pageUrl':url});
        }
      }
      if(!mounted)return;
      setState(() { translations=found; loading=false; if(found.isEmpty) error='Не удалось получить список озвучек. Возможно, HDRezka заблокировала запрос или изменила разметку.'; });
    } catch(e) { if(mounted)setState((){loading=false;error=e.toString();}); }
  }
  Future<Map<String,dynamic>> api(Map<String,dynamic> item,String action,{int season=1,int episode=1}) async {
    final body=<String,String>{'id':item['id'].toString(),'translator_id':item['translatorId'].toString(),'action':action};
    if(action=='get_stream'){body['season']='$season';body['episode']='$episode';}
    final r=await http.post(Uri.parse(base+'/ajax/get_cdn_series/'),headers:{
      'User-Agent':ua,'Referer':item['pageUrl'],'Origin':base,'X-Requested-With':'XMLHttpRequest',
      'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','Accept':'application/json, */*'
    },body:body).timeout(const Duration(seconds:25));
    if(r.statusCode!=200)throw Exception('HDRezka API HTTP '+r.statusCode.toString());
    final d=jsonDecode(r.body);
    if(d is! Map<String,dynamic>)throw Exception('Некорректный ответ HDRezka');
    return d;
  }
  String decode(String raw) {
    var v=raw.trim(); if(v.startsWith('[')||v.startsWith('http'))return v;
    v=v.replaceAll('#h','');
    const salts=['IyMjI14hISMjIUBA','QEBAQEAhIyMhXl5e','JCQhIUAkJEBeIUAjJCRA','JCQjISFAIyFAIyM=','Xl5eIUAjIyEhIyM='];
    for(var i=0;i<12&&v.contains('//_//');i++){
      final p=v.indexOf('//_//'), tail=v.substring(p+5);
      final salt=salts.where((x)=>tail.startsWith(x)).firstOrNull;
      v=v.substring(0,p)+(salt==null?(tail.length>16?tail.substring(16):''):tail.substring(salt.length));
    }
    try{return utf8.decode(base64.decode(base64.normalize(v)));}catch(_){return v;}
  }
  List<String> links(String raw) {
    final decoded=decode(raw);
    final found=RegExp(r'\[(?:\d{3,4}p|auto)\](https?://[^\s,]+)',caseSensitive:false).allMatches(decoded).map((m)=>m.group(1)!).toList();
    if(found.isNotEmpty)return found;
    return RegExp(r'https?://[^\s,]+').allMatches(decoded).map((m)=>m.group(0)!).toList();
  }
  Future<void> choose(Map<String,dynamic> item) async {
    try {
      final d=await api(item,widget.mediaType=='tv'?'get_episodes':'get_movie');
      final raw=(d['url']??'').toString();
      final urls=links(raw);
      if(urls.isNotEmpty) {
        if(!mounted)return;
        Navigator.push(context,MaterialPageRoute<void>(builder:(_)=>CustomStreamPlayer(title:widget.title,streamUrl:urls.first)));
        return;
      }
      final episodes=<Map<String,int>>[];
      final html=(d['seasons']??d['episodes']??'').toString();
      final ep=RegExp(r'''data-season=["'](\d+)["'][\s\S]*?data-episode=["'](\d+)["']''');
      for(final m in ep.allMatches(html)){episodes.add({'season':int.parse(m.group(1)!),'episode':int.parse(m.group(2)!)});}
      if(episodes.isEmpty)throw Exception('Не удалось получить серии/поток для этой озвучки.');
      if(!mounted)return;
      Navigator.push(context,MaterialPageRoute<void>(builder:(_)=>EpisodePickerPage(title:widget.title,episodes:episodes,onPlay:(season,episode)async{
        final stream=await api(item,'get_stream',season:season,episode:episode);
        final found=links((stream['url']??'').toString());
        if(found.isEmpty)throw Exception('Ссылка на серию не найдена');
        return found.first;
      })));
    }catch(e){if(mounted)ScaffoldMessenger.of(context).showSnackBar(SnackBar(content:Text(e.toString())));}
  }
  @override
  Widget build(BuildContext context)=>Scaffold(backgroundColor:const Color(0xFF080A0F),appBar:AppBar(backgroundColor:const Color(0xFF10131A),foregroundColor:Colors.white,title:Text('Озвучки • '+widget.title),actions:[IconButton(onPressed:loading?null:_search,icon:const Icon(Icons.refresh))]),body:ListView(padding:const EdgeInsets.all(16),children:[
    Text(widget.title,style:const TextStyle(color:Colors.white,fontSize:22,fontWeight:FontWeight.bold)),
    if(widget.year.isNotEmpty)Text(widget.year,style:const TextStyle(color:Colors.white60)),
    if(loading)const Center(child:CircularProgressIndicator(color:Color(0xFFE65A32))),
    if(error!=null&&!loading)Text(error!,style:const TextStyle(color:Colors.orangeAccent)),
    ...translations.map((x)=>Card(color:const Color(0xFF171B24),child:ListTile(leading:const Icon(Icons.record_voice_over,color:Colors.white),title:Text(x['name'].toString(),style:const TextStyle(color:Colors.white)),subtitle:const Text('Прямой поток • HDRezka',style:TextStyle(color:Colors.white54)),trailing:const Icon(Icons.play_circle_fill,color:Color(0xFFE65A32)),onTap:()=>choose(x))))
  ]));
}
class EpisodePickerPage extends StatelessWidget {
  final String title; final List<Map<String,int>> episodes; final Future<String> Function(int,int) onPlay;
  const EpisodePickerPage({super.key,required this.title,required this.episodes,required this.onPlay});
  @override
  Widget build(BuildContext context)=>Scaffold(backgroundColor:const Color(0xFF080A0F),appBar:AppBar(backgroundColor:const Color(0xFF10131A),foregroundColor:Colors.white,title:Text(title)),body:ListView(children:episodes.map((e)=>ListTile(leading:const Icon(Icons.play_circle_outline,color:Color(0xFFE65A32)),title:Text('Сезон '+e['season'].toString()+' • Серия '+e['episode'].toString(),style:const TextStyle(color:Colors.white)),onTap:()async{try{final url=await onPlay(e['season']!,e['episode']!);if(!context.mounted)return;Navigator.push(context,MaterialPageRoute<void>(builder:(_)=>CustomStreamPlayer(title:title,streamUrl:url)));}catch(err){if(context.mounted)ScaffoldMessenger.of(context).showSnackBar(SnackBar(content:Text(err.toString())));}})).toList()));
}
class CustomStreamPlayer extends StatefulWidget {
  final String title,streamUrl;
  const CustomStreamPlayer({super.key,required this.title,required this.streamUrl});
  @override
  State<CustomStreamPlayer> createState()=>_CustomStreamPlayerState();
}
class _CustomStreamPlayerState extends State<CustomStreamPlayer>{
  VideoPlayerController? player; String? error;
  @override
  void initState(){super.initState();_start();}
  Future<void> _start()async{try{final c=VideoPlayerController.networkUrl(Uri.parse(widget.streamUrl),httpHeaders:{'User-Agent':'Mozilla/5.0','Referer':'https://hdrezka.ag/'});player=c;await c.initialize();if(!mounted)return;setState((){});await c.play();}catch(e){if(mounted)setState(()=>error=e.toString());}}
  @override
  void dispose(){player?.dispose();super.dispose();}
  @override
  Widget build(BuildContext context){final p=player;return Scaffold(backgroundColor:Colors.black,appBar:AppBar(backgroundColor:Colors.black,foregroundColor:Colors.white,title:Text(widget.title)),body:Center(child:error!=null?Padding(padding:const EdgeInsets.all(20),child:Text('Ошибка запуска потока: '+error!,style:const TextStyle(color:Colors.white70))):p==null||!p.value.isInitialized?const CircularProgressIndicator(color:Color(0xFFE65A32)):AspectRatio(aspectRatio:p.value.aspectRatio,child:Stack(alignment:Alignment.bottomCenter,children:[VideoPlayer(p),VideoProgressIndicator(p,allowScrubbing:true,colors:const VideoProgressColors(playedColor:Color(0xFFE65A32),bufferedColor:Colors.white38,backgroundColor:Colors.white12)),Positioned(right:10,bottom:20,child:IconButton(icon:Icon(p.value.isPlaying?Icons.pause_circle:Icons.play_circle,color:Colors.white,size:42),onPressed:()=>setState(()=>p.value.isPlaying?p.pause():p.play())))]))));}
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
), '');
  if (proxy.isEmpty) return Uri.https('api.themoviedb.org', path, params);
  return Uri.parse('$proxy/api$path').replace(queryParameters: params);
}
String tmdbImageUrl(String path) {
  final proxy = tmdbProxyBase.trim().replaceAll(RegExp(r'/+

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
  List<String> favoriteIds = [];

  @override
  void initState() { super.initState(); _loadFavorites(); load(); }

  Future<void> _loadFavorites() async {
    final prefs = await SharedPreferences.getInstance();
    if (mounted) setState(() => favoriteIds = prefs.getStringList('cinema_favorites') ?? []);
  }
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
      final cacheKey = 'tmdb_catalog_' + path + '_' + (params['query'] ?? '') + '_' + (params['with_genres'] ?? '');
      final prefs = await SharedPreferences.getInstance();
      final cached = prefs.getString(cacheKey);
      if (cached != null && mounted) {
        final cachedData = jsonDecode(cached) as Map<String, dynamic>;
        setState(() { items = (cachedData['results'] as List? ?? []).where((x) => x['media_type'] != 'person').toList(); loading = false; });
      }
      final response = await http.get(Uri.https('api.themoviedb.org', '/3' + path, params)).timeout(const Duration(seconds: 15));
      if (response.statusCode != 200) throw Exception('TMDB HTTP ' + response.statusCode.toString());
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      await prefs.setString(cacheKey, response.body);
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
  bool isFavorite = false;

  @override
  void initState() { super.initState(); _loadDetails(); _loadFavorite(); }

  String get _favoriteKey => widget.mediaType + '_' + widget.item['id'].toString();

  Future<void> _loadFavorite() async {
    final prefs = await SharedPreferences.getInstance();
    if (mounted) setState(() => isFavorite = (prefs.getStringList('cinema_favorites') ?? []).contains(_favoriteKey));
  }

  Future<void> _toggleFavorite() async {
    final prefs = await SharedPreferences.getInstance();
    final ids = prefs.getStringList('cinema_favorites') ?? [];
    if (ids.contains(_favoriteKey)) { ids.remove(_favoriteKey); } else { ids.add(_favoriteKey); }
    await prefs.setStringList('cinema_favorites', ids);
    if (mounted) setState(() => isFavorite = ids.contains(_favoriteKey));
  }

  void _watch() {
    Navigator.of(context).push(MaterialPageRoute<void>(
      builder: (_) => VideoSourcesPage(
        title: _title,
        originalTitle: (details?['original_title'] ?? details?['original_name'] ?? widget.item['original_title'] ?? widget.item['original_name'] ?? _title).toString(),
        year: _date.length >= 4 ? _date.substring(0, 4) : '',
        mediaType: widget.mediaType,
      ),
    ));
  }

  Future<void> _loadDetails() async {
    try {
      final id = widget.item['id'];
      final uri = Uri.https('api.themoviedb.org', '/3/' + widget.mediaType + '/' + id.toString(), {
        'api_key': tmdbKey, 'language': 'ru-RU', 'append_to_response': 'credits',
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
    final tagline = (details?['tagline'] ?? '').toString();
    final status = (details?['status'] ?? '').toString();
    final countryList = (details?['production_countries'] as List? ?? const []).map((x) => (x['name'] ?? '').toString()).where((x) => x.isNotEmpty).take(2).join(', ');
    final cast = (details?['credits']?['cast'] as List? ?? const []).take(3).map((x) => (x['name'] ?? '').toString()).where((x) => x.isNotEmpty).join(' • ');
    final screenWidth = MediaQuery.of(context).size.width;
    final isTv = screenWidth >= 900;
    final compact = screenWidth < 600;

    final favoriteButton = OutlinedButton.icon(
      autofocus: isTv,
      onPressed: _toggleFavorite,
      icon: Icon(isFavorite ? Icons.favorite : Icons.favorite_border,
        color: isFavorite ? Colors.pinkAccent : Colors.white, size: isTv ? 27 : 21),
      label: Text(isFavorite ? 'В избранном' : 'В избранное',
        style: TextStyle(color: Colors.white, fontSize: isTv ? 20 : 15, fontWeight: FontWeight.w600)),
      style: OutlinedButton.styleFrom(
        minimumSize: Size(isTv ? 250 : 0, isTv ? 64 : 52),
        padding: EdgeInsets.symmetric(horizontal: isTv ? 28 : 16, vertical: isTv ? 18 : 14),
        side: const BorderSide(color: Colors.white70, width: 1.5),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
    final watchButton = FilledButton.icon(
      onPressed: _watch,
      icon: Icon(Icons.play_arrow_rounded, color: Colors.white, size: isTv ? 30 : 22),
      label: Text('Смотреть', style: TextStyle(color: Colors.white,
        fontSize: isTv ? 21 : 16, fontWeight: FontWeight.bold)),
      style: FilledButton.styleFrom(
        minimumSize: Size(isTv ? 230 : 0, isTv ? 64 : 52),
        padding: EdgeInsets.symmetric(horizontal: isTv ? 32 : 18, vertical: isTv ? 18 : 14),
        backgroundColor: const Color(0xFFE65A32),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );

    return Scaffold(
      backgroundColor: const Color(0xFF080A0F),
      body: Stack(fit: StackFit.expand, children: [
        if (backdrop.isNotEmpty)
          ImageFiltered(
            imageFilter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
            child: Image.network(
              'https://image.tmdb.org/t/p/w1280' + backdrop,
              fit: BoxFit.cover,
              cacheWidth: 1600,
              gaplessPlayback: true,
              errorBuilder: (_, __, ___) => const SizedBox.shrink(),
            ),
          ),
        const DecoratedBox(decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0x99060910), Color(0xE6080A0F), Color(0xFF080A0F)],
            stops: [0.0, 0.48, 1.0],
          ),
        )),
        SafeArea(child: Column(children: [
          SizedBox(
            height: 54,
            child: Row(children: [
              IconButton(
                icon: const Icon(Icons.arrow_back_rounded, color: Colors.white, size: 28),
                onPressed: () => Navigator.pop(context),
              ),
              const SizedBox(width: 8),
              Expanded(child: Text(
                _title,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w700),
              )),
              const SizedBox(width: 16),
            ]),
          ),
          Expanded(child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: EdgeInsets.fromLTRB(compact ? 16 : 42, 12, compact ? 16 : 42, 34),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              LayoutBuilder(builder: (context, constraints) {
                final posterWidth = (constraints.maxWidth * (compact ? 0.38 : isTv ? 0.25 : 0.23)).clamp(112.0, isTv ? 340.0 : 260.0);
                final posterHeight = posterWidth * 1.48;
                return Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  if (poster.isNotEmpty)
                    ClipRRect(borderRadius: BorderRadius.circular(12), child: Image.network(
                      'https://image.tmdb.org/t/p/w500' + poster, width: posterWidth, height: posterHeight,
                      fit: BoxFit.cover, cacheWidth: 520, filterQuality: FilterQuality.medium, gaplessPlayback: true,
                      errorBuilder: (_, __, ___) => Container(width: posterWidth, height: posterHeight, color: const Color(0xFF1B1F29), child: const Icon(Icons.movie_outlined, color: Colors.white54, size: 42)),
                    )),
                  SizedBox(width: compact ? 16 : 34),
                  Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text(_title, maxLines: 3, overflow: TextOverflow.ellipsis, style: TextStyle(color: Colors.white, fontSize: compact ? 22 : 34, fontWeight: FontWeight.w800, height: 1.12)),
                    if (tagline.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 7), child: Text(tagline, style: const TextStyle(color: Colors.white60, fontStyle: FontStyle.italic))),
                    SizedBox(height: 12),
                    Wrap(spacing: 8, runSpacing: 8, children: [
                      _chip(year, Icons.calendar_today_outlined), _chip('★ ' + rating, Icons.star_outline_rounded),
                      if (runtime != null) _chip(runtime.toString() + ' мин.', Icons.schedule_rounded),
                      if (details?['number_of_seasons'] != null) _chip(details!['number_of_seasons'].toString() + ' сез.', Icons.tv_outlined),
                      if (details?['number_of_episodes'] != null) _chip(details!['number_of_episodes'].toString() + ' сер.', Icons.video_library_outlined),
                      if (status.isNotEmpty) _chip(status, Icons.info_outline),
                    ]),
                    if (genres.isNotEmpty) ...[SizedBox(height: 12), Wrap(spacing: 7, runSpacing: 7, children: genres.take(compact ? 4 : 7).map((g) => _chip((g['name'] ?? '').toString(), Icons.local_offer_outlined)).toList())],
                  ])),
                ]);
              }),
              SizedBox(height: 22),
              Wrap(spacing: 12, runSpacing: 10, children: [
                watchButton,
                favoriteButton,
              ]),
              SizedBox(height: 24),
              Text('О фильме', style: TextStyle(color: Colors.white, fontSize: compact ? 19 : 24, fontWeight: FontWeight.bold)),
              SizedBox(height: 9),
              Text(overview, style: TextStyle(color: Colors.white.withOpacity(.86), fontSize: compact ? 14 : 17, height: 1.55)),
              if (countryList.isNotEmpty || details?['original_language'] != null) ...[
                SizedBox(height: 18),
                Text([if (countryList.isNotEmpty) countryList, if (details?['original_language'] != null) 'Язык: ' + details!['original_language'].toString().toUpperCase()].join('  •  '), style: const TextStyle(color: Colors.white60, fontSize: 13)),
              ],
              if (cast.isNotEmpty) ...[
                SizedBox(height: 18),
                Text('В ролях', style: TextStyle(color: Colors.white, fontSize: compact ? 18 : 22, fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                Text(cast, style: const TextStyle(color: Colors.white70, fontSize: 14)),
              ],
              if (loading) const Padding(padding: EdgeInsets.only(top: 18), child: LinearProgressIndicator(color: Colors.white38, backgroundColor: Colors.white12)),
              if (error != null) const Padding(padding: EdgeInsets.only(top: 10), child: Text('Не удалось загрузить данные', style: TextStyle(color: Colors.white54))),
            ]),
          )),
        ])),
      ]),
    );
  }

  Widget _chip(String text, IconData icon) => Container(
    padding: EdgeInsets.symmetric(horizontal: 11.w, vertical: 8.h),
    decoration: BoxDecoration(color: Colors.white.withOpacity(.09), borderRadius: BorderRadius.circular(20.r)),
    child: Row(mainAxisSize: MainAxisSize.min, children: [
      Icon(icon, color: Colors.white70, size: 15.sp), SizedBox(width: 6.w),
      Text(text, style: TextStyle(color: Colors.white, fontSize: 13.sp)),
    ]),
  );

}

class VideoSourcesPage extends StatefulWidget {
  final String title;
  final String originalTitle;
  final String year;
  final String mediaType;
  const VideoSourcesPage({super.key, required this.title, required this.originalTitle, required this.year, required this.mediaType});
  @override
  State<VideoSourcesPage> createState() => _VideoSourcesPageState();
}

class _VideoSourcesPageState extends State<VideoSourcesPage> {
  List<Map<String, dynamic>> results = [];
  bool loading = false;
  String? error;

  @override
  void initState() { super.initState(); _search(); }

  String _normalize(String value) => value.toLowerCase().replaceAll(RegExp(r'[^a-zа-яё0-9]'), '');

  Future<void> _search() async {
    setState(() { loading = true; error = null; results = []; });
    try {
      final uri = Uri.https('hdrezka.ag', '/engine/ajax/search.php', {'q': widget.title});
      final response = await http.get(uri, headers: {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html,*/*',
      }).timeout(const Duration(seconds: 20));
      if (response.statusCode != 200) {
        throw Exception('HDRezka HTTP ' + response.statusCode.toString() + '. Возможно, сайт временно недоступен.');
      }

      final found = <Map<String, dynamic>>[];
      final pattern = RegExp(r'''<a[^>]+href=["']([^"']+)["'][^>]*>([\s\S]*?)</a>''', caseSensitive: false);
      final titleNeedle = _normalize(widget.title);
      final originalNeedle = _normalize(widget.originalTitle);
      for (final match in pattern.allMatches(response.body)) {
        final link = (match.group(1) ?? '').trim();
        final name = (match.group(2) ?? '')
            .replaceAll(RegExp(r'<[^>]*>'), ' ')
            .replaceAll('&nbsp;', ' ')
            .replaceAll('&amp;', '&')
            .trim();
        if (!link.startsWith('http') || name.isEmpty) continue;
        final normalizedName = _normalize(name);
        final titleMatch = (titleNeedle.isNotEmpty &&
                (normalizedName.contains(titleNeedle) || titleNeedle.contains(normalizedName))) ||
            (originalNeedle.isNotEmpty &&
                (normalizedName.contains(originalNeedle) || originalNeedle.contains(normalizedName)));
        if (titleMatch) {
          found.add({
            'translation': {'title': 'HDRezka'},
            'quality': name,
            'link': link,
            'provider': 'HDRezka',
          });
        }
      }

      final seen = <String>{};
      final unique = found.where((item) => seen.add((item['link'] ?? '').toString())).toList();
      if (!mounted) return;
      setState(() {
        results = unique;
        loading = false;
        if (unique.isEmpty) {
          error = 'На HDRezka ничего не найдено. Проверьте название или попробуйте позже.';
        }
      });
    } catch (e) {
      if (mounted) setState(() { loading = false; error = e.toString(); });
    }
  }

  @override
  Widget build(BuildContext context) {
    final isTv = MediaQuery.of(context).size.width >= 900;
    return Scaffold(
      backgroundColor: const Color(0xFF080A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF10131A),
        foregroundColor: Colors.white,
        title: const Text('HDRezka'),
        actions: [IconButton(
          tooltip: 'Повторить поиск',
          onPressed: loading ? null : _search,
          icon: const Icon(Icons.refresh),
        )],
      ),
      body: Center(child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 820),
        child: ListView(padding: EdgeInsets.all(isTv ? 28 : 18), children: [
          Text(widget.title, style: TextStyle(color: Colors.white, fontSize: isTv ? 28 : 21, fontWeight: FontWeight.bold)),
          if (widget.year.isNotEmpty)
            Padding(padding: const EdgeInsets.only(top: 6), child: Text(widget.year, style: const TextStyle(color: Colors.white60))),
          const SizedBox(height: 18),
          const Text('Поиск видео на HDRezka по названию', style: TextStyle(color: Colors.white54, fontSize: 13)),
          const SizedBox(height: 16),
          if (loading)
            const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator(color: Color(0xFFE65A32)))),
          if (error != null && !loading)
            Padding(padding: const EdgeInsets.all(12), child: Text(error!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.orangeAccent))),
          ...results.map((item) {
            final name = (item['translation'] as Map)['title'].toString();
            final quality = (item['quality'] ?? 'Результат HDRezka').toString();
            final link = (item['link'] ?? '').toString();
            return Container(
              margin: const EdgeInsets.only(bottom: 10),
              decoration: BoxDecoration(color: const Color(0xFF171B24), borderRadius: BorderRadius.circular(14), border: Border.all(color: Colors.white10)),
              child: ListTile(
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                leading: const CircleAvatar(backgroundColor: Color(0xFF303746), child: Icon(Icons.movie, color: Colors.white)),
                title: Text(name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
                subtitle: Text(quality, style: const TextStyle(color: Colors.white60)),
                trailing: const Icon(Icons.play_circle_fill, color: Color(0xFFE65A32), size: 30),
                onTap: () => Navigator.of(context).push(MaterialPageRoute<void>(
                  builder: (_) => KodikPlayerPage(title: widget.title, url: link),
                )),
              ),
            );
          }),
        ]),
      )),
    );
  }
}

class KodikPlayerPage extends StatefulWidget {
  final String title;
  final String url;
  const KodikPlayerPage({super.key, required this.title, required this.url});
  @override
  State<KodikPlayerPage> createState() => _KodikPlayerPageState();
}

class _KodikPlayerPageState extends State<KodikPlayerPage> {
  late final WebViewController controller;
  @override
  void initState() {
    super.initState();
    controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(NavigationDelegate(onWebResourceError: (error) {}))
      ..loadRequest(Uri.parse(widget.url));
  }
  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: Colors.black,
    appBar: AppBar(backgroundColor: const Color(0xFF10131A), foregroundColor: Colors.white, title: Text(widget.title)),
    body: WebViewWidget(controller: controller),
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
), '');
  if (proxy.isEmpty) return 'https://image.tmdb.org' + path;
  return '$proxy/image$path';
}

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
  List<String> favoriteIds = [];

  @override
  void initState() { super.initState(); _loadFavorites(); load(); }

  Future<void> _loadFavorites() async {
    final prefs = await SharedPreferences.getInstance();
    if (mounted) setState(() => favoriteIds = prefs.getStringList('cinema_favorites') ?? []);
  }
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
      final cacheKey = 'tmdb_catalog_' + path + '_' + (params['query'] ?? '') + '_' + (params['with_genres'] ?? '');
      final prefs = await SharedPreferences.getInstance();
      final cached = prefs.getString(cacheKey);
      if (cached != null && mounted) {
        final cachedData = jsonDecode(cached) as Map<String, dynamic>;
        setState(() { items = (cachedData['results'] as List? ?? []).where((x) => x['media_type'] != 'person').toList(); loading = false; });
      }
      final response = await http.get(Uri.https('api.themoviedb.org', '/3' + path, params)).timeout(const Duration(seconds: 15));
      if (response.statusCode != 200) throw Exception('TMDB HTTP ' + response.statusCode.toString());
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      await prefs.setString(cacheKey, response.body);
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
  bool isFavorite = false;

  @override
  void initState() { super.initState(); _loadDetails(); _loadFavorite(); }

  String get _favoriteKey => widget.mediaType + '_' + widget.item['id'].toString();

  Future<void> _loadFavorite() async {
    final prefs = await SharedPreferences.getInstance();
    if (mounted) setState(() => isFavorite = (prefs.getStringList('cinema_favorites') ?? []).contains(_favoriteKey));
  }

  Future<void> _toggleFavorite() async {
    final prefs = await SharedPreferences.getInstance();
    final ids = prefs.getStringList('cinema_favorites') ?? [];
    if (ids.contains(_favoriteKey)) { ids.remove(_favoriteKey); } else { ids.add(_favoriteKey); }
    await prefs.setStringList('cinema_favorites', ids);
    if (mounted) setState(() => isFavorite = ids.contains(_favoriteKey));
  }

  void _watch() {
    Navigator.of(context).push(MaterialPageRoute<void>(
      builder: (_) => VideoSourcesPage(
        title: _title,
        originalTitle: (details?['original_title'] ?? details?['original_name'] ?? widget.item['original_title'] ?? widget.item['original_name'] ?? _title).toString(),
        year: _date.length >= 4 ? _date.substring(0, 4) : '',
        mediaType: widget.mediaType,
      ),
    ));
  }

  Future<void> _loadDetails() async {
    try {
      final id = widget.item['id'];
      final uri = Uri.https('api.themoviedb.org', '/3/' + widget.mediaType + '/' + id.toString(), {
        'api_key': tmdbKey, 'language': 'ru-RU', 'append_to_response': 'credits',
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
    final tagline = (details?['tagline'] ?? '').toString();
    final status = (details?['status'] ?? '').toString();
    final countryList = (details?['production_countries'] as List? ?? const []).map((x) => (x['name'] ?? '').toString()).where((x) => x.isNotEmpty).take(2).join(', ');
    final cast = (details?['credits']?['cast'] as List? ?? const []).take(3).map((x) => (x['name'] ?? '').toString()).where((x) => x.isNotEmpty).join(' • ');
    final screenWidth = MediaQuery.of(context).size.width;
    final isTv = screenWidth >= 900;
    final compact = screenWidth < 600;

    final favoriteButton = OutlinedButton.icon(
      autofocus: isTv,
      onPressed: _toggleFavorite,
      icon: Icon(isFavorite ? Icons.favorite : Icons.favorite_border,
        color: isFavorite ? Colors.pinkAccent : Colors.white, size: isTv ? 27 : 21),
      label: Text(isFavorite ? 'В избранном' : 'В избранное',
        style: TextStyle(color: Colors.white, fontSize: isTv ? 20 : 15, fontWeight: FontWeight.w600)),
      style: OutlinedButton.styleFrom(
        minimumSize: Size(isTv ? 250 : 0, isTv ? 64 : 52),
        padding: EdgeInsets.symmetric(horizontal: isTv ? 28 : 16, vertical: isTv ? 18 : 14),
        side: const BorderSide(color: Colors.white70, width: 1.5),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
    final watchButton = FilledButton.icon(
      onPressed: _watch,
      icon: Icon(Icons.play_arrow_rounded, color: Colors.white, size: isTv ? 30 : 22),
      label: Text('Смотреть', style: TextStyle(color: Colors.white,
        fontSize: isTv ? 21 : 16, fontWeight: FontWeight.bold)),
      style: FilledButton.styleFrom(
        minimumSize: Size(isTv ? 230 : 0, isTv ? 64 : 52),
        padding: EdgeInsets.symmetric(horizontal: isTv ? 32 : 18, vertical: isTv ? 18 : 14),
        backgroundColor: const Color(0xFFE65A32),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );

    return Scaffold(
      backgroundColor: const Color(0xFF080A0F),
      body: Stack(fit: StackFit.expand, children: [
        if (backdrop.isNotEmpty)
          ImageFiltered(
            imageFilter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
            child: Image.network(
              'https://image.tmdb.org/t/p/w1280' + backdrop,
              fit: BoxFit.cover,
              cacheWidth: 1600,
              gaplessPlayback: true,
              errorBuilder: (_, __, ___) => const SizedBox.shrink(),
            ),
          ),
        const DecoratedBox(decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0x99060910), Color(0xE6080A0F), Color(0xFF080A0F)],
            stops: [0.0, 0.48, 1.0],
          ),
        )),
        SafeArea(child: Column(children: [
          SizedBox(
            height: 54,
            child: Row(children: [
              IconButton(
                icon: const Icon(Icons.arrow_back_rounded, color: Colors.white, size: 28),
                onPressed: () => Navigator.pop(context),
              ),
              const SizedBox(width: 8),
              Expanded(child: Text(
                _title,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w700),
              )),
              const SizedBox(width: 16),
            ]),
          ),
          Expanded(child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: EdgeInsets.fromLTRB(compact ? 16 : 42, 12, compact ? 16 : 42, 34),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              LayoutBuilder(builder: (context, constraints) {
                final posterWidth = (constraints.maxWidth * (compact ? 0.38 : isTv ? 0.25 : 0.23)).clamp(112.0, isTv ? 340.0 : 260.0);
                final posterHeight = posterWidth * 1.48;
                return Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  if (poster.isNotEmpty)
                    ClipRRect(borderRadius: BorderRadius.circular(12), child: Image.network(
                      'https://image.tmdb.org/t/p/w500' + poster, width: posterWidth, height: posterHeight,
                      fit: BoxFit.cover, cacheWidth: 520, filterQuality: FilterQuality.medium, gaplessPlayback: true,
                      errorBuilder: (_, __, ___) => Container(width: posterWidth, height: posterHeight, color: const Color(0xFF1B1F29), child: const Icon(Icons.movie_outlined, color: Colors.white54, size: 42)),
                    )),
                  SizedBox(width: compact ? 16 : 34),
                  Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text(_title, maxLines: 3, overflow: TextOverflow.ellipsis, style: TextStyle(color: Colors.white, fontSize: compact ? 22 : 34, fontWeight: FontWeight.w800, height: 1.12)),
                    if (tagline.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 7), child: Text(tagline, style: const TextStyle(color: Colors.white60, fontStyle: FontStyle.italic))),
                    SizedBox(height: 12),
                    Wrap(spacing: 8, runSpacing: 8, children: [
                      _chip(year, Icons.calendar_today_outlined), _chip('★ ' + rating, Icons.star_outline_rounded),
                      if (runtime != null) _chip(runtime.toString() + ' мин.', Icons.schedule_rounded),
                      if (details?['number_of_seasons'] != null) _chip(details!['number_of_seasons'].toString() + ' сез.', Icons.tv_outlined),
                      if (details?['number_of_episodes'] != null) _chip(details!['number_of_episodes'].toString() + ' сер.', Icons.video_library_outlined),
                      if (status.isNotEmpty) _chip(status, Icons.info_outline),
                    ]),
                    if (genres.isNotEmpty) ...[SizedBox(height: 12), Wrap(spacing: 7, runSpacing: 7, children: genres.take(compact ? 4 : 7).map((g) => _chip((g['name'] ?? '').toString(), Icons.local_offer_outlined)).toList())],
                  ])),
                ]);
              }),
              SizedBox(height: 22),
              Wrap(spacing: 12, runSpacing: 10, children: [
                watchButton,
                favoriteButton,
              ]),
              SizedBox(height: 24),
              Text('О фильме', style: TextStyle(color: Colors.white, fontSize: compact ? 19 : 24, fontWeight: FontWeight.bold)),
              SizedBox(height: 9),
              Text(overview, style: TextStyle(color: Colors.white.withOpacity(.86), fontSize: compact ? 14 : 17, height: 1.55)),
              if (countryList.isNotEmpty || details?['original_language'] != null) ...[
                SizedBox(height: 18),
                Text([if (countryList.isNotEmpty) countryList, if (details?['original_language'] != null) 'Язык: ' + details!['original_language'].toString().toUpperCase()].join('  •  '), style: const TextStyle(color: Colors.white60, fontSize: 13)),
              ],
              if (cast.isNotEmpty) ...[
                SizedBox(height: 18),
                Text('В ролях', style: TextStyle(color: Colors.white, fontSize: compact ? 18 : 22, fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                Text(cast, style: const TextStyle(color: Colors.white70, fontSize: 14)),
              ],
              if (loading) const Padding(padding: EdgeInsets.only(top: 18), child: LinearProgressIndicator(color: Colors.white38, backgroundColor: Colors.white12)),
              if (error != null) const Padding(padding: EdgeInsets.only(top: 10), child: Text('Не удалось загрузить данные', style: TextStyle(color: Colors.white54))),
            ]),
          )),
        ])),
      ]),
    );
  }

  Widget _chip(String text, IconData icon) => Container(
    padding: EdgeInsets.symmetric(horizontal: 11.w, vertical: 8.h),
    decoration: BoxDecoration(color: Colors.white.withOpacity(.09), borderRadius: BorderRadius.circular(20.r)),
    child: Row(mainAxisSize: MainAxisSize.min, children: [
      Icon(icon, color: Colors.white70, size: 15.sp), SizedBox(width: 6.w),
      Text(text, style: TextStyle(color: Colors.white, fontSize: 13.sp)),
    ]),
  );

}

class VideoSourcesPage extends StatefulWidget {
  final String title;
  final String originalTitle;
  final String year;
  final String mediaType;
  const VideoSourcesPage({super.key, required this.title, required this.originalTitle, required this.year, required this.mediaType});
  @override
  State<VideoSourcesPage> createState() => _VideoSourcesPageState();
}

class _VideoSourcesPageState extends State<VideoSourcesPage> {
  List<Map<String, dynamic>> results = [];
  bool loading = false;
  String? error;

  @override
  void initState() { super.initState(); _search(); }

  String _normalize(String value) => value.toLowerCase().replaceAll(RegExp(r'[^a-zа-яё0-9]'), '');

  Future<void> _search() async {
    setState(() { loading = true; error = null; results = []; });
    try {
      final uri = Uri.https('hdrezka.ag', '/engine/ajax/search.php', {'q': widget.title});
      final response = await http.get(uri, headers: {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html,*/*',
      }).timeout(const Duration(seconds: 20));
      if (response.statusCode != 200) {
        throw Exception('HDRezka HTTP ' + response.statusCode.toString() + '. Возможно, сайт временно недоступен.');
      }

      final found = <Map<String, dynamic>>[];
      final pattern = RegExp(r'''<a[^>]+href=["']([^"']+)["'][^>]*>([\s\S]*?)</a>''', caseSensitive: false);
      final titleNeedle = _normalize(widget.title);
      final originalNeedle = _normalize(widget.originalTitle);
      for (final match in pattern.allMatches(response.body)) {
        final link = (match.group(1) ?? '').trim();
        final name = (match.group(2) ?? '')
            .replaceAll(RegExp(r'<[^>]*>'), ' ')
            .replaceAll('&nbsp;', ' ')
            .replaceAll('&amp;', '&')
            .trim();
        if (!link.startsWith('http') || name.isEmpty) continue;
        final normalizedName = _normalize(name);
        final titleMatch = (titleNeedle.isNotEmpty &&
                (normalizedName.contains(titleNeedle) || titleNeedle.contains(normalizedName))) ||
            (originalNeedle.isNotEmpty &&
                (normalizedName.contains(originalNeedle) || originalNeedle.contains(normalizedName)));
        if (titleMatch) {
          found.add({
            'translation': {'title': 'HDRezka'},
            'quality': name,
            'link': link,
            'provider': 'HDRezka',
          });
        }
      }

      final seen = <String>{};
      final unique = found.where((item) => seen.add((item['link'] ?? '').toString())).toList();
      if (!mounted) return;
      setState(() {
        results = unique;
        loading = false;
        if (unique.isEmpty) {
          error = 'На HDRezka ничего не найдено. Проверьте название или попробуйте позже.';
        }
      });
    } catch (e) {
      if (mounted) setState(() { loading = false; error = e.toString(); });
    }
  }

  @override
  Widget build(BuildContext context) {
    final isTv = MediaQuery.of(context).size.width >= 900;
    return Scaffold(
      backgroundColor: const Color(0xFF080A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF10131A),
        foregroundColor: Colors.white,
        title: const Text('HDRezka'),
        actions: [IconButton(
          tooltip: 'Повторить поиск',
          onPressed: loading ? null : _search,
          icon: const Icon(Icons.refresh),
        )],
      ),
      body: Center(child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 820),
        child: ListView(padding: EdgeInsets.all(isTv ? 28 : 18), children: [
          Text(widget.title, style: TextStyle(color: Colors.white, fontSize: isTv ? 28 : 21, fontWeight: FontWeight.bold)),
          if (widget.year.isNotEmpty)
            Padding(padding: const EdgeInsets.only(top: 6), child: Text(widget.year, style: const TextStyle(color: Colors.white60))),
          const SizedBox(height: 18),
          const Text('Поиск видео на HDRezka по названию', style: TextStyle(color: Colors.white54, fontSize: 13)),
          const SizedBox(height: 16),
          if (loading)
            const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator(color: Color(0xFFE65A32)))),
          if (error != null && !loading)
            Padding(padding: const EdgeInsets.all(12), child: Text(error!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.orangeAccent))),
          ...results.map((item) {
            final name = (item['translation'] as Map)['title'].toString();
            final quality = (item['quality'] ?? 'Результат HDRezka').toString();
            final link = (item['link'] ?? '').toString();
            return Container(
              margin: const EdgeInsets.only(bottom: 10),
              decoration: BoxDecoration(color: const Color(0xFF171B24), borderRadius: BorderRadius.circular(14), border: Border.all(color: Colors.white10)),
              child: ListTile(
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                leading: const CircleAvatar(backgroundColor: Color(0xFF303746), child: Icon(Icons.movie, color: Colors.white)),
                title: Text(name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
                subtitle: Text(quality, style: const TextStyle(color: Colors.white60)),
                trailing: const Icon(Icons.play_circle_fill, color: Color(0xFFE65A32), size: 30),
                onTap: () => Navigator.of(context).push(MaterialPageRoute<void>(
                  builder: (_) => KodikPlayerPage(title: widget.title, url: link),
                )),
              ),
            );
          }),
        ]),
      )),
    );
  }
}

class KodikPlayerPage extends StatefulWidget {
  final String title;
  final String url;
  const KodikPlayerPage({super.key, required this.title, required this.url});
  @override
  State<KodikPlayerPage> createState() => _KodikPlayerPageState();
}

class _KodikPlayerPageState extends State<KodikPlayerPage> {
  late final WebViewController controller;
  @override
  void initState() {
    super.initState();
    controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(NavigationDelegate(onWebResourceError: (error) {}))
      ..loadRequest(Uri.parse(widget.url));
  }
  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: Colors.black,
    appBar: AppBar(backgroundColor: const Color(0xFF10131A), foregroundColor: Colors.white, title: Text(widget.title)),
    body: WebViewWidget(controller: controller),
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
