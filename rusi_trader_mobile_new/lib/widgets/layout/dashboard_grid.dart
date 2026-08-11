import 'package:flutter/material.dart';

class DashboardGrid extends StatelessWidget {
  final List<Widget> children;

  const DashboardGrid({
    super.key,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    //==========================================================
    // MOBILE
    //
    // Android uses a vertical scroll layout so cards can take
    // their natural height. This prevents Bottom Overflow on
    // narrow phone screens.
    //==========================================================

    if (Theme.of(context).platform == TargetPlatform.android) {
      return ListView.separated(
        padding: EdgeInsets.zero,
        itemCount: children.length,
        separatorBuilder: (context, index) => const SizedBox(height: 16),
        itemBuilder: (context, index) {
          return children[index];
        },
      );
    }

    //==========================================================
    // DESKTOP
    //
    // Preserve the existing responsive grid.
    //==========================================================

    return LayoutBuilder(
      builder: (context, constraints) {
        int columns;

        //--------------------------------------------------
        // Responsive Columns
        //--------------------------------------------------

        if (constraints.maxWidth >= 1800) {
          columns = 4;
        } else if (constraints.maxWidth >= 1300) {
          columns = 3;
        } else if (constraints.maxWidth >= 900) {
          columns = 2;
        } else {
          columns = 1;
        }

        return GridView.builder(
          padding: EdgeInsets.zero,
          itemCount: children.length,
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: columns,

            crossAxisSpacing: 20,

            mainAxisSpacing: 20,

            //--------------------------------------------------
            // Increased card height to avoid overflow
            //--------------------------------------------------

            childAspectRatio: 1.45,
          ),
          itemBuilder: (context, index) {
            return children[index];
          },
        );
      },
    );
  }
}
