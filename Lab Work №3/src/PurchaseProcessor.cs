// SOLID: Interface Segregation - маленький специализированный интерфейс
public interface IPurchaseProcessor
{
    Task<PurchaseResult> ProcessPurchaseAsync(PurchaseRequest request);
}

// SOLID: Single Responsibility - только обработка покупки
public class PurchaseProcessor : IPurchaseProcessor
{
    private readonly IPaymentClient _paymentClient;
    private readonly IProductCatalog _productCatalog;
    private readonly IInventoryClient _inventoryClient;
    private readonly ILogger<PurchaseProcessor> _logger;

    // SOLID: Dependency Inversion - зависимости через интерфейсы
    public PurchaseProcessor(
        IPaymentClient paymentClient,
        IProductCatalog productCatalog,
        IInventoryClient inventoryClient,
        ILogger<PurchaseProcessor> logger)
    {
        _paymentClient = paymentClient;
        _productCatalog = productCatalog;
        _inventoryClient = inventoryClient;
        _logger = logger;
    }

    // KISS: Один метод - одна четкая ответственность
    public async Task<PurchaseResult> ProcessPurchaseAsync(PurchaseRequest request)
    {
        _logger.LogInformation("Processing purchase: User={UserId}, Item={ItemId}", 
            request.UserId, request.ItemId);

        try
        {
            // 1. Получение информации о товаре
            var product = await _productCatalog.GetItemAsync(request.ItemId);
            if (product == null)
            {
                return PurchaseResult.Failure("Товар не найден");
            }

            // YAGNI: Простая проверка, без сложной бизнес-логики
            if (!product.IsAvailable)
            {
                return PurchaseResult.Failure("Товар недоступен");
            }

            // 2. Обработка платежа
            var paymentResult = await _paymentClient.CreatePaymentAsync(
                request.UserId, 
                product.Price, 
                request.PaymentMethod);

            if (!paymentResult.Success)
            {
                return PurchaseResult.Failure($"Ошибка платежа: {paymentResult.Error}");
            }

            // 3. Добавление предмета в инвентарь
            var inventoryResult = await _inventoryClient.AddItemAsync(
                request.UserId, 
                request.ItemId, 
                paymentResult.TransactionId);

            if (!inventoryResult.Success)
            {
                // DRY: Повторное использование кода отмены платежа
                await TryRefundPaymentAsync(paymentResult.TransactionId);
                return PurchaseResult.Failure("Не удалось добавить предмет в инвентарь");
            }

            // 4. Успешный результат
            return PurchaseResult.Success(paymentResult.TransactionId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error during purchase processing");
            return PurchaseResult.Failure("Внутренняя ошибка сервера");
        }
    }

    // DRY: Вынесенная логика возврата платежа
    private async Task TryRefundPaymentAsync(string transactionId)
    {
        try
        {
            await _paymentClient.RefundPaymentAsync(transactionId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to refund payment: {TransactionId}", transactionId);
        }
    }
}

// KISS: Простые модели данных
public class PurchaseRequest
{
    public string UserId { get; set; } = string.Empty;
    public string ItemId { get; set; } = string.Empty;
    public string PaymentMethod { get; set; } = string.Empty;
}

// SOLID: Single Responsibility - отдельный класс для результата
public class PurchaseResult
{
    public bool Success { get; }
    public string? Error { get; }
    public string? TransactionId { get; }

    private PurchaseResult(bool success, string? error, string? transactionId)
    {
        Success = success;
        Error = error;
        TransactionId = transactionId;
    }

    // DRY: Фабричные методы вместо дублирования конструкторов
    public static PurchaseResult Success(string transactionId)
        => new PurchaseResult(true, null, transactionId);

    public static PurchaseResult Failure(string error)
        => new PurchaseResult(false, error, null);
}
