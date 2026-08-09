import 'package:flutter/material.dart';

class QuickActionCard extends StatelessWidget {
  const QuickActionCard({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xff151515),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
      ),
      child: Padding(
        padding: const EdgeInsets.all(22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [

            const Row(
              children: [

                Icon(
                  Icons.flash_on,
                  color: Colors.amber,
                ),

                SizedBox(width: 8),

                Text(
                  "Quick Action",
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),

            const Spacer(),

            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: () {
                  debugPrint("BUY");
                },
                icon: const Icon(Icons.trending_up),
                label: const Text("BUY"),
              ),
            ),

            const SizedBox(height: 12),

            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                style: FilledButton.styleFrom(
                  backgroundColor: Colors.red,
                ),
                onPressed: () {
                  debugPrint("SELL");
                },
                icon: const Icon(Icons.trending_down),
                label: const Text("SELL"),
              ),
            ),

            const SizedBox(height: 12),

            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {
                  debugPrint("EXIT");
                },
                icon: const Icon(Icons.close),
                label: const Text("EXIT POSITION"),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
