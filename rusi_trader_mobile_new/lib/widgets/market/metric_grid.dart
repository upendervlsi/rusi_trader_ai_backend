import 'package:flutter/material.dart';

class MetricGrid extends StatelessWidget {
  final List<Widget> children;

  const MetricGrid({
    super.key,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      physics:
          const NeverScrollableScrollPhysics(),

      shrinkWrap: true,

      crossAxisCount: 2,

      crossAxisSpacing: 12,

      mainAxisSpacing: 12,

      childAspectRatio: 2.1,

      children: children,
    );
  }
}
