import 'package:flutter/material.dart';

import '../../models/dashboard_model.dart';

class MarketPulseCard extends StatelessWidget {
  final List<DashboardMarketModel> markets;

  final String? strongestMarket;

  final double? strongestConfidence;

  final ValueChanged<DashboardMarketModel>? onMarketTap;

  const MarketPulseCard({
    super.key,
    required this.markets,
    required this.strongestMarket,
    required this.strongestConfidence,
    this.onMarketTap,
  });

  //============================================================
  // SIGNAL COLOR
  //============================================================

  Color _signalColor(
    String signal,
  ) {
    switch (signal.toUpperCase()) {
      case "BUY":
        return Colors.green;

      case "SELL":
        return Colors.red;

      case "HOLD":
        return Colors.orange;

      case "WAIT":
      default:
        return Colors.grey;
    }
  }

  //============================================================
  // CONFIDENCE
  //============================================================

  String _confidenceText(
    DashboardMarketModel market,
  ) {
    if (market.confidence == null) {
      return "--";
    }

    return "${market.confidence!.round()}%";
  }

  //============================================================
  // STATUS
  //============================================================

  String _statusText(
    DashboardMarketModel market,
  ) {
    if (market.status.isEmpty) {
      return "WAITING";
    }

    return market.status.toUpperCase();
  }

  //============================================================
  // BUILD
  //============================================================

  @override
  Widget build(
    BuildContext context,
  ) {
    return Card(
      elevation: 3,

      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),

      child: Padding(
        padding: const EdgeInsets.all(18),

        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.start,

          children: [

            //==================================================
            // HEADER
            //==================================================

            Row(
              children: [

                const Icon(
                  Icons.radar,
                  size: 22,
                ),

                const SizedBox(width: 10),

                const Expanded(
                  child: Text(
                    "Market Pulse",
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight:
                          FontWeight.bold,
                    ),
                  ),
                ),

                if (strongestMarket != null &&
                    strongestConfidence != null)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 5,
                    ),

                    decoration:
                        BoxDecoration(
                      borderRadius:
                          BorderRadius.circular(20),

                      border: Border.all(),
                    ),

                    child: Text(
                      "TOP "
                      "${strongestConfidence!.round()}%",
                      style:
                          const TextStyle(
                        fontSize: 11,
                        fontWeight:
                            FontWeight.bold,
                      ),
                    ),
                  ),
              ],
            ),

            const SizedBox(height: 5),

            const Text(
              "Complete market view",
              style: TextStyle(
                fontSize: 12,
              ),
            ),

            const SizedBox(height: 12),

            //==================================================
            // COLUMN HEADERS
            //==================================================

            Padding(
              padding:
                  const EdgeInsets.symmetric(
                horizontal: 12,
              ),

              child: Row(
                children: const [

                  Expanded(
                    flex: 4,
                    child: Text(
                      "MARKET",
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight:
                            FontWeight.bold,
                      ),
                    ),
                  ),

                  Expanded(
                    flex: 2,
                    child: Text(
                      "SIGNAL",
                      textAlign:
                          TextAlign.center,
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight:
                            FontWeight.bold,
                      ),
                    ),
                  ),

                  Expanded(
                    flex: 2,
                    child: Text(
                      "CONF.",
                      textAlign:
                          TextAlign.right,
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight:
                            FontWeight.bold,
                      ),
                    ),
                  ),

                  SizedBox(width: 20),
                ],
              ),
            ),

            const SizedBox(height: 5),

            //==================================================
            // MARKET ROWS
            //==================================================

            if (markets.isEmpty)
              const Padding(
                padding:
                    EdgeInsets.symmetric(
                  vertical: 20,
                ),

                child: Center(
                  child: Text(
                    "Market data waiting...",
                  ),
                ),
              )
            else
              ...markets.map(
                (market) {

                  final isStrongest =
                      market.displayName ==
                      strongestMarket;

                  final signalColor =
                      _signalColor(
                    market.signal,
                  );

                  return _MarketPulseRow(
                    market: market,

                    signalColor:
                        signalColor,

                    highlighted:
                        isStrongest,

                    status:
                        _statusText(
                      market,
                    ),

                    confidence:
                        _confidenceText(
                      market,
                    ),

                    onTap:
                        onMarketTap == null
                            ? null
                            : () =>
                                onMarketTap!(
                                  market,
                                ),
                  );
                },
              ),
          ],
        ),
      ),
    );
  }
}


//================================================================
// MARKET PULSE ROW
//================================================================

class _MarketPulseRow
    extends StatelessWidget {

  final DashboardMarketModel market;

  final Color signalColor;

  final bool highlighted;

  final String status;

  final String confidence;

  final VoidCallback? onTap;

  const _MarketPulseRow({
    required this.market,
    required this.signalColor,
    required this.highlighted,
    required this.status,
    required this.confidence,
    required this.onTap,
  });

  @override
  Widget build(
    BuildContext context,
  ) {
    return InkWell(
      onTap: onTap,

      borderRadius:
          BorderRadius.circular(10),

      child: Container(
        margin:
            const EdgeInsets.only(
          bottom: 6,
        ),

        padding:
            const EdgeInsets.symmetric(
          horizontal: 12,
          vertical: 8,
        ),

        decoration:
            BoxDecoration(
          borderRadius:
              BorderRadius.circular(10),

          border: Border.all(
            color: highlighted
                ? signalColor
                : Colors.grey.shade800,

            width:
                highlighted ? 1.5 : 1,
          ),

          color: highlighted
              ? signalColor.withOpacity(0.08)
              : null,
        ),

        child: Row(
          children: [

            //================================================
            // MARKET
            //================================================

            Expanded(
              flex: 4,

              child: Row(
                children: [

                  Container(
                    width: 7,
                    height: 7,

                    decoration:
                        BoxDecoration(
                      shape:
                          BoxShape.circle,

                      color:
                          signalColor,
                    ),
                  ),

                  const SizedBox(
                    width: 8,
                  ),

                  Expanded(
                    child: Text(
                      market.displayName,

                      overflow:
                          TextOverflow.ellipsis,

                      style:
                          const TextStyle(
                        fontSize: 13,
                        fontWeight:
                            FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            //================================================
            // SIGNAL
            //================================================

            Expanded(
              flex: 2,

              child: Column(
                children: [

                  Text(
                    market.signal
                        .toUpperCase(),

                    textAlign:
                        TextAlign.center,

                    style:
                        TextStyle(
                      color:
                          signalColor,

                      fontSize: 13,

                      fontWeight:
                          FontWeight.bold,
                    ),
                  ),

                  Text(
                    status,

                    textAlign:
                        TextAlign.center,

                    style:
                        const TextStyle(
                      fontSize: 8,
                    ),
                  ),
                ],
              ),
            ),

            //================================================
            // CONFIDENCE
            //================================================

            Expanded(
              flex: 2,

              child: Text(
                confidence,

                textAlign:
                    TextAlign.right,

                style:
                    const TextStyle(
                  fontSize: 13,
                  fontWeight:
                      FontWeight.bold,
                ),
              ),
            ),

            const SizedBox(
              width: 6,
            ),

            const Icon(
              Icons.chevron_right,
              size: 18,
            ),
          ],
        ),
      ),
    );
  }
}
