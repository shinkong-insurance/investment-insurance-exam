class Question {
  final int id;
  final int chapterId;
  final int questionNo;
  final String question;
  final List<String> options;
  final int answer;
  final String explanation;

  const Question({
    required this.id,
    required this.chapterId,
    required this.questionNo,
    required this.question,
    required this.options,
    required this.answer,
    required this.explanation,
  });

  factory Question.fromJson(Map<String, dynamic> json) => Question(
    id: json['id'],
    chapterId: json['chapterId'],
    questionNo: json['questionNo'],
    question: json['question'],
    options: List<String>.from(json['options']),
    answer: json['answer'],
    explanation: json['explanation'] ?? '',
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'chapterId': chapterId,
    'questionNo': questionNo,
    'question': question,
    'options': options,
    'answer': answer,
    'explanation': explanation,
  };

  /// 顯示用章節標籤：模考題（201/202）顯示科目模考，其餘顯示「第 N 章」。
  String get chapterLabel => chapterLabelFor(chapterId);
}

String chapterLabelFor(int chapterId) {
  if (chapterId == 201) return '第一科模考';
  if (chapterId == 202) return '第二科模考';
  return '第 ${chapterId % 100} 章';
}
