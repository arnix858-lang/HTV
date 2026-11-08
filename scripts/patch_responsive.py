from pathlib import Path
def patch(path, old, new, label):
 p=Path(path); s=p.read_text()
 if old not in s: raise SystemExit("Pattern missing: "+label)
 p.write_text(s.replace(old,new,1))
patch("lib/pages/panel/widgets/iptv_info.dart", """            Observer(
              builder: (_) => Text(
                iptvStore.currentIptv.name,
                style: AppTheme.text(fg, 60.sp, weight: FontWeight.bold),
              ),
            ),""", """            Expanded(
              child: Observer(
                builder: (_) => Text(
                  iptvStore.currentIptv.name,
                  style: AppTheme.text(fg, 60.sp, weight: FontWeight.bold),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ),""", "channel title")
p=Path("lib/pages/panel/widgets/iptv_info.dart")
s=p.read_text().replace("SizedBox(width: 40.w),","SizedBox(width: 12.w),",1)
s=s.replace("""            style: AppTheme.text(programmeColor, 30.sp),
          ),""","""            style: AppTheme.text(programmeColor, 30.sp),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),""",2)
p.write_text(s)
patch("lib/pages/settings/widgets/settings.dart", """              Text(
                item.title,
                style: AppTheme.text(textColor, 30.sp),
              ),
              Text(
                item.value(),
                style: AppTheme.text(textColor, 30.sp),
              ),""", """              Expanded(child: Text(item.title, style: AppTheme.text(textColor, 30.sp), maxLines: 1, overflow: TextOverflow.ellipsis)),
              SizedBox(width: 8.w),
              Flexible(child: Text(item.value(), style: AppTheme.text(textColor, 26.sp), maxLines: 1, overflow: TextOverflow.ellipsis, textAlign: TextAlign.end)),""", "settings title/value")
patch("lib/pages/settings/widgets/app_info.dart", """          builder: (_) => Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,""", """          builder: (_) => Wrap(
            crossAxisAlignment: WrapCrossAlignment.center,
            spacing: 12.w,
            runSpacing: 4.h,""", "app info row")
p=Path("lib/pages/settings/widgets/app_info.dart"); p.write_text(p.read_text().replace("SizedBox(width: 20.w),","SizedBox(width: 4.w),",2))
patch("lib/pages/panel/view.dart", """      child: SizedBox(
        width: 360.w,
        child: Container(
          padding: const EdgeInsets.only(left: 40).r,
          child: _buildPanelContent(),
        ),
      ),""", """      child: LayoutBuilder(builder: (context, constraints) {
        final panelWidth = (MediaQuery.sizeOf(context).width * 0.42).clamp(300.0, 760.0);
        return SizedBox(width: panelWidth, child: Padding(
          padding: EdgeInsets.only(left: 24.w, right: 12.w, top: 12.h, bottom: 12.h),
          child: _buildPanelContent(),
        ));
      }),""", "panel width")
print("Responsive layout patch applied")
