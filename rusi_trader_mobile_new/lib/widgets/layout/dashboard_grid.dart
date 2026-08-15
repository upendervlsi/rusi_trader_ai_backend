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
    // Vertical layout.
    // Cards use their natural height.
    //==========================================================

    if (Theme.of(context).platform == TargetPlatform.android) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (int i = 0; i < children.length; i++) ...[
            children[i],
            if (i != children.length - 1)
              const SizedBox(height: 16),
          ],
        ],
      );
    }

    //==========================================================
    // DESKTOP
    //
    // Responsive grid.
    //
    // Market Pulse is intentionally allowed to be taller
    // because it contains the complete market-wide view.
    //==========================================================

    return LayoutBuilder(
      builder: (context, constraints) {
        int columns;

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

          shrinkWrap: true,

          physics: const NeverScrollableScrollPhysics(),

          itemCount: children.length,

          gridDelegate:
              SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: columns,

            crossAxisSpacing: 20,

            mainAxisSpacing: 20,

            // Give dashboard cards enough vertical space.
            childAspectRatio: 1.15,
          ),

          itemBuilder: (
            context,
            index,
          ) {
            return children[index];
          },
        );
      },
    );
  }
}
