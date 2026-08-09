/*
============================================================

RUSI Trader AI

Professional Execution Card

============================================================
*/

import 'package:flutter/material.dart';

import '../../models/execution_model.dart';

class ExecutionCard extends StatelessWidget {
  final ExecutionModel execution;

  const ExecutionCard({
    super.key,
    required this.execution,
  });

  Color get statusColor {
    return execution.approved
        ? Colors.green
        : Colors.red;
  }

  IconData get statusIcon {
    return execution.approved
        ? Icons.verified
        : Icons.block;
  }

  @override
  Widget build(
    BuildContext context,
  ) {
    return Card(
      elevation: 5,
      shape: RoundedRectangleBorder(
        borderRadius:
            BorderRadius.circular(16),
      ),
      child: Padding(
        padding:
            const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.start,
          children: [

            //--------------------------------------
            // Header
            //--------------------------------------

            Row(
              children: [

                Icon(
                  statusIcon,
                  color: statusColor,
                  size: 36,
                ),

                const SizedBox(
                  width: 12,
                ),

                Expanded(
                  child: Column(
                    crossAxisAlignment:
                        CrossAxisAlignment.start,
                    children: [

                      Text(
                        execution.approved
                            ? "Execution Approved"
                            : "Execution Blocked",
                        style: TextStyle(
                          fontSize: 22,
                          fontWeight:
                              FontWeight.bold,
                          color: statusColor,
                        ),
                      ),

                      const SizedBox(
                        height: 4,
                      ),

                      Text(
                        execution.reason,
                        style:
                            const TextStyle(
                          color:
                              Colors.grey,
                        ),
                      ),

                    ],
                  ),
                ),

              ],
            ),

            const SizedBox(
              height: 20,
            ),
            //--------------------------------------
            // Validation Checklist
            //--------------------------------------

            _buildCheck(
              "Confidence",
              execution.confidenceOk,
            ),

            _buildCheck(
              "Market Open",
              execution.marketOpen,
            ),

            _buildCheck(
              "Risk Validation",
              execution.riskOk,
            ),

            _buildCheck(
              "Margin Available",
              execution.marginOk,
            ),

            _buildCheck(
              "Cooldown",
              execution.cooldownOk,
            ),

            _buildCheck(
              "Daily Limit",
              execution.dailyLimitOk,
            ),

            _buildCheck(
              "Position Check",
              execution.positionOk,
            ),

          ],
        ),
      ),
    );
  }

  //--------------------------------------------------
  // Validation Row
  //--------------------------------------------------

  Widget _buildCheck(
    String title,
    bool passed,
  ) {
    return ListTile(
      dense: true,

      contentPadding:
          EdgeInsets.zero,

      leading: Icon(
        passed
            ? Icons.check_circle
            : Icons.cancel,
        color: passed
            ? Colors.green
            : Colors.red,
      ),

      title: Text(title),

      trailing: Text(
        passed ? "PASS" : "FAIL",
        style: TextStyle(
          color: passed
              ? Colors.green
              : Colors.red,
          fontWeight:
              FontWeight.bold,
        ),
      ),
    );
  }
}
