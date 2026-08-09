import 'package:flutter/material.dart';

class ActionButton extends StatelessWidget {

  final String text;

  final IconData icon;

  final Color color;

  final VoidCallback onPressed;

  const ActionButton({
    super.key,
    required this.text,
    required this.icon,
    required this.color,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {

    return SizedBox(
      width: double.infinity,
      child: FilledButton.icon(
        style: FilledButton.styleFrom(
          backgroundColor: color,
          minimumSize: const Size(
            double.infinity,
            48,
          ),
        ),
        onPressed: onPressed,
        icon: Icon(icon),
        label: Text(text),
      ),
    );
  }

}
