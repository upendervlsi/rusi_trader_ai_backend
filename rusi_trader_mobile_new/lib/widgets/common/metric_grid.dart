import 'package:flutter/material.dart';

class MetricGrid extends StatelessWidget {
  final List<Widget> children;

  const MetricGrid({
    super.key,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: children.map((child) {
        return SizedBox(
          width: 260,
          height: 110,
          child: child,
        );
      }).toList(),
    );
  }
}
