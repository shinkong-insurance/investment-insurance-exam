import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:investment_insurance_exam/features/home/home_page.dart';
import 'package:investment_insurance_exam/providers/auth_provider.dart';
import 'package:investment_insurance_exam/providers/question_provider.dart';
import 'package:investment_insurance_exam/providers/section_provider.dart';
import 'package:investment_insurance_exam/providers/user_data_provider.dart';

class _FakeAuth extends ExamAuthNotifier {
  @override
  Future<ExamAuthState> build() async =>
      const ExamAuthState(isLoggedIn: false, isLoading: false);
}

void main() {
  Future<GoRouter> pump(WidgetTester tester) async {
    tester.view.physicalSize = const Size(900, 3000);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
    final router = GoRouter(routes: [
      GoRoute(path: '/', builder: (_, __) => const HomePage()),
      GoRoute(
          path: '/exam',
          builder: (_, s) => Text('EXAM ${s.uri.queryParameters}')),
    ]);
    await tester.pumpWidget(ProviderScope(
      overrides: [
        examAuthProvider.overrideWith(_FakeAuth.new),
        wrongIdsProvider.overrideWith((_) async => <int>[]),
        favoriteIdsProvider.overrideWith((_) async => <int>[]),
        allQuestionsProvider.overrideWith((_) async => []),
        allSectionsProvider.overrideWith((_) async => []),
        chaptersProvider.overrideWith((_) async => []),
      ],
      child: MaterialApp.router(routerConfig: router),
    ));
    await tester.pumpAndSettle();
    return router;
  }

  testWidgets('shows both subject mock cards', (tester) async {
    await pump(tester);
    expect(find.text('科目模考'), findsOneWidget);
    expect(find.text('第一科模考（95 題）'), findsOneWidget);
    expect(find.text('第二科模考（181 題）'), findsOneWidget);
    expect(find.textContaining('保險實務'), findsNothing);
  });

  testWidgets('tapping subject 1 navigates to /exam', (tester) async {
    await pump(tester);
    await tester.tap(find.text('第一科模考（95 題）'));
    await tester.pumpAndSettle();
    expect(find.textContaining('count: 95'), findsOneWidget);
    expect(find.textContaining('chapter: 201'), findsOneWidget);
    expect(find.textContaining('paper: 第一科'), findsOneWidget);
  });
}
