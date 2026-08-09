import 'package:flutter/material.dart';

class PageTemplate extends StatelessWidget {
  final String title;
  final Widget? child;

  const PageTemplate({
    super.key,
    required this.title,
    this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [

          Text(
            title,
            style: const TextStyle(
              fontSize: 30,
              fontWeight: FontWeight.bold,
            ),
          ),

          const SizedBox(height: 20),

          Expanded(
            child: child ??
                const Center(
                  child: Text(
                    "Coming Soon...",
                    style: TextStyle(
                      fontSize: 20,
                    ),
                  ),
                ),
          ),
        ],
      ),
    );
  }
}
