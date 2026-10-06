import 'package:flutter_test/flutter_test.dart';
import 'package:investment_insurance_exam/models/question.dart';

void main() {
  test('chapterLabelFor maps mock-exam and chapter ids', () {
    expect(chapterLabelFor(201), '第一科模考');
    expect(chapterLabelFor(202), '第二科模考');
    expect(chapterLabelFor(101), '第 1 章');
    expect(chapterLabelFor(110), '第 10 章');
  });
}
