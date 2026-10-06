import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:investment_insurance_exam/features/exam/exam_result_page.dart';
import 'package:investment_insurance_exam/models/question.dart';

void main() {
  testWidgets('result review renders a 3-option question without throwing',
      (tester) async {
    tester.view.physicalSize = const Size(800, 3000);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
    const q = Question(
      id: 105012,
      chapterId: 105,
      questionNo: 12,
      question: '三個選項的題目',
      options: ['甲', '乙', '丙'],
      answer: 2,
      explanation: '',
    );
    await tester.pumpWidget(MaterialApp(
      home: ExamResultPage(result: {
        'score': 0,
        'correct': 0,
        'total': 1,
        'questions': [q],
        'answers': <int, int>{0: 1},
      }),
    ));
    await tester.pumpAndSettle();
    // Expand review tiles if any
    for (final t in tester.widgetList<ExpansionTile>(find.byType(ExpansionTile)).toList()) {
      await tester.tap(find.byWidget(t));
    }
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
    expect(find.text('丙'), findsOneWidget);
    expect(find.text('(4) '), findsNothing);
  });
}
