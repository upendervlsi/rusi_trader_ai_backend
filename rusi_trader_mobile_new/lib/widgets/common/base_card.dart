import 'package:flutter/material.dart';

class BaseCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final Widget child;
  final List<Widget>? actions;

  const BaseCard({
    super.key,
    required this.title,
    required this.icon,
    required this.child,
    this.actions,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      color: const Color(0xff151515),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
      ),
      clipBehavior: Clip.antiAlias,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            //--------------------------------------------------
            // Header
            //--------------------------------------------------

            Row(
              children: [
                Icon(
                  icon,
                  color: Colors.lightBlueAccent,
                  size: 24,
                ),

                const SizedBox(width: 10),

                Expanded(
                  child: Text(
                    title,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),

                if (actions != null) ...actions!,
              ],
            ),

            const SizedBox(height: 18),

            //--------------------------------------------------
            // Body
            //--------------------------------------------------

            child,
          ],
        ),
      ),
    );
  }
}
