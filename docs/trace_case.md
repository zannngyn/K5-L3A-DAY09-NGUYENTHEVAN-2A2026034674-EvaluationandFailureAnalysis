# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

## Case đã điều tra: `seeded_regression C-002@11`

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, thuộc run `E-seeded_regression-20261117-01dc` |
| Triệu chứng | `lab8 grader: FAIL (status resolved != denied)`. Reply nói `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."`, ledger ghi `refund_vnd=20000`, `refund_count=1`, trong khi nhãn mong đợi `refund_vnd=0`, `refund_count=0`, `status=denied`. |
| Bước sai đầu tiên | Event #3 `model_override` — `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event #1 (`handoff`) tạo handoff hợp lệ không lộ secret; Event #2 (`investigator`) gọi `lookup_order` trả đúng dữ liệu DB (`O-202`, `status="delivered"`, `delay_days=2`, chưa đủ điều kiện hoàn tiền). Mọi dữ liệu trước Event #3 đều đúng; ngay tại Event #3 agent tin số `5` trong ticket để ghi đè `delay_days=2` của DB, dẫn tới Event #4 tính sai `quote=20000` và ghi nhầm ledger. |
| Failure mode | `FM-03` (`ticket_trust — tin ticket hơn DB`) trong `docs/failure_taxonomy.md` |
| Đối chứng | Trên shape `fixed C-002@11`: không có event `model_override`; sau Event #2 (`investigator`), Event #3 (`quote`) tính trực tiếp từ DB ra `{"amount_vnd": 0, "reason": "no_entitlement"}`, Event #4 (`reply`) từ chối đúng chính sách (`ledger=0`, `status=denied`). |
| Regression test | `src/tests/test_lab9_trace_case.py::test_trace_case_c002_seed11_fixed_passes_and_regression_fails` — dùng `DbFactKept` và `RefundAmountCorrect` khẳng định `seeded_regression C-002@11` fail cả hai và `fixed C-002@11` pass cả hai. |
| Chưa chắc chắn | Trace không ghi lại prompt thô hoặc reasoning nội bộ của bước `parse` trong MockLLM, nhưng event `model_override` đủ chứng minh quyết định ghi đè DB đã xảy ra trước khi tính `quote`. |
