import 'package:flutter/material.dart';

class DashboardCard extends StatelessWidget {
  final String title;
  final Widget child;
  final IconData icon;

  const DashboardCard({
    super.key,
    required this.title,
    required this.child,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {

    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
      ),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.start,
          children: [

            Row(
              children: [

                Icon(icon),

                const SizedBox(width: 10),

                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),

              ],
            ),

            const SizedBox(height: 20),

            Expanded(
              child: child,
            ),

          ],
        ),
      ),
    );
  }
}
