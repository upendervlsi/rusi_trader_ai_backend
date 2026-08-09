/*
============================================================

RUSI Trader AI

AI Decision Screen

MVVM Version

============================================================
*/

import 'package:flutter/material.dart';

import '../../viewmodels/ai_decision_view_model.dart';

import '../../widgets/ai/decision_header.dart';
import '../../widgets/ai/execution_card.dart';
import '../../widgets/ai/trade_plan_card.dart';
import '../../widgets/ai/ai_reasoning_card.dart';

class AIDecisionScreen extends StatefulWidget {
  const AIDecisionScreen({
    super.key,
  });

  @override
  State<AIDecisionScreen> createState() =>
      _AIDecisionScreenState();
}

class _AIDecisionScreenState
    extends State<AIDecisionScreen> {

  //----------------------------------------------------------
  // ViewModel
  //----------------------------------------------------------

  final AIDecisionViewModel vm =
      AIDecisionViewModel();

  @override
  void initState() {
    super.initState();

    vm.load();
  }

  @override
  Widget build(
    BuildContext context,
  ) {
    return AnimatedBuilder(

      animation: vm,

      builder: (
        context,
        _,
      ) {

        //------------------------------------------------------
        // Loading
        //------------------------------------------------------

        if (vm.loading) {

          return const Scaffold(

            body: Center(

              child:
                  CircularProgressIndicator(),

            ),

          );

        }

        //------------------------------------------------------
        // Error
        //------------------------------------------------------

        if (vm.error != null) {

          return Scaffold(

            appBar: AppBar(

              title: const Text(
                "AI Decision Center",
              ),

            ),

            body: Center(

              child: Text(
                vm.error!,
              ),

            ),

          );

        }

        //------------------------------------------------------
        // No Data
        //------------------------------------------------------

        if (vm.decision == null) {

          return const Scaffold(

            body: Center(

              child: Text(
                "No AI Decision Available",
              ),

            ),

          );

        }

        final trade =
            vm.decision!.tradePlan;

        final execution =
            vm.decision!.execution;
        return Scaffold(

          appBar: AppBar(

            centerTitle: true,

            title: const Text(
              "AI Decision Center",
            ),

          ),

          body: RefreshIndicator(

            onRefresh: vm.refresh,

            child: ListView(

              padding:
                  const EdgeInsets.all(16),

              children: [

                //------------------------------------------------
                // AI Recommendation
                //------------------------------------------------

                DecisionHeader(
                  trade: trade,
                ),

                const SizedBox(
                  height: 16,
                ),

                //------------------------------------------------
                // Execution Status
                //------------------------------------------------

                ExecutionCard(
                  execution: execution,
                ),

                const SizedBox(
                  height: 16,
                ),

                //------------------------------------------------
                // Trade Plan
                //------------------------------------------------

                TradePlanCard(
                  trade: trade,
                ),

                const SizedBox(
                  height: 16,
                ),

                //------------------------------------------------
                // AI Reasoning
                //------------------------------------------------

                AIReasoningCard(
                  reasons:
                      trade.reasons,
                ),

                const SizedBox(
                  height: 30,
                ),

              ],

            ),

          ),

        );

      },

    );

  }

}
