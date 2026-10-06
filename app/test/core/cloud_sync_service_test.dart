import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:investment_insurance_exam/core/services/cloud_sync_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('init() picks up an LK session written after app start; reset() clears it', () async {
    SharedPreferences.setMockInitialValues({});
    expect(await CloudSyncService.init(), isFalse);
    expect(CloudSyncService.isLkMode, isFalse);

    // 模擬同一頁面 session 內剛註冊 / 金鑰登入完成
    SharedPreferences.setMockInitialValues({
      'inv_lk_logged_in': true,
      'inv_lk_key_id': 'key-1',
      'inv_lk_key_code': 'SK-2026-ABCD-1234',
      'inv_lk_expires_at':
          DateTime.now().add(const Duration(days: 60)).toIso8601String(),
    });
    expect(await CloudSyncService.init(), isTrue);
    expect(CloudSyncService.isLkMode, isTrue);

    CloudSyncService.reset();
    expect(CloudSyncService.isLkMode, isFalse);
  });
}
