"""
送信制御ドメインサービス

営業メール等の自動送信が可能かどうかを判定するビジネスロジックを提供します。
送信禁止設定（曜日・時間帯・日付）に基づいて送信可否を判断します。
"""
from datetime import datetime

from src.domain.entities.no_send_setting_entity import NoSendSettingEntity


class SendControlService:
    """
    送信制御ドメインサービス

    送信禁止設定に基づいて、指定された日時に送信可能かどうかを判定します。
    """

    @staticmethod
    def can_send_at(
        settings: list[NoSendSettingEntity],
        check_datetime: datetime,
    ) -> tuple[bool, str | None]:
        """
        指定された日時に送信可能かどうかを判定する

        Args:
            settings: 送信禁止設定のリスト
            check_datetime: チェック対象の日時（timezone aware）

        Returns:
            tuple[bool, str | None]: (送信可能か, 送信不可の理由)
            - 送信可能な場合: (True, None)
            - 送信不可な場合: (False, "禁止理由の説明")

        ビジネスルール:
            - 設定が空の場合は常に送信可能
            - is_enabled=Falseの設定は無視
            - deleted_at が設定されている設定は無視
            - 複数の設定に該当する場合、最初の設定の理由を返す
            - 曜日設定: ISO 8601準拠（月曜=1, 日曜=7）
            - 時間帯設定: 日跨ぎ（22:00-6:00）に対応
        """
        for setting in settings:
            # 無効な設定または論理削除済みの設定はスキップ
            if not setting.is_active():
                continue

            # 曜日チェック
            if setting.is_day_of_week_setting():
                if setting.day_of_week_list is None:
                    continue

                weekday = check_datetime.isoweekday()  # ISO 8601: 月曜=1, 日曜=7
                if weekday in setting.day_of_week_list:
                    return False, f"禁止曜日: {setting.name}"

            # 時間帯チェック（日跨ぎ対応）
            elif setting.is_time_range_setting():
                if setting.time_start is None or setting.time_end is None:
                    continue

                current_time = check_datetime.time()
                time_start = setting.time_start
                time_end = setting.time_end

                # 日を跨ぐ場合（例: 22:00 - 6:00）
                if time_start > time_end:
                    # 現在時刻が開始時刻以降、または終了時刻以前
                    if current_time >= time_start or current_time < time_end:
                        return False, f"禁止時間帯: {setting.name}"
                else:
                    # 通常の時間帯（例: 9:00 - 17:00）
                    if time_start <= current_time < time_end:
                        return False, f"禁止時間帯: {setting.name}"

            # 日付チェック
            elif setting.is_specific_date_setting():
                current_date = check_datetime.date()

                # 特定日付のチェック
                if setting.specific_date is not None:
                    if current_date == setting.specific_date:
                        return False, f"禁止日: {setting.name}"

                # 日付範囲のチェック
                if (
                    setting.date_range_start is not None
                    and setting.date_range_end is not None
                ):
                    if setting.date_range_start <= current_date <= setting.date_range_end:
                        return False, f"禁止期間: {setting.name}"

        # すべてのチェックを通過した場合、送信可能
        return True, None
