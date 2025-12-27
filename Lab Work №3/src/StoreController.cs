[ApiController]
[Route("api/store")]
[Authorize]
public class StoreController : ControllerBase
{
    private readonly IPurchaseProcessor _purchaseProcessor;
    private readonly IProductCatalog _productCatalog;
    private readonly ILogger<StoreController> _logger;

    public StoreController(
        IPurchaseProcessor purchaseProcessor,
        IProductCatalog productCatalog,
        ILogger<StoreController> logger)
    {
        _purchaseProcessor = purchaseProcessor;
        _productCatalog = productCatalog;
        _logger = logger;
    }

    [HttpPost("purchase")]
    public async Task<IActionResult> Purchase([FromBody] PurchaseRequest requestData)
    {
        // KISS: Простая валидация
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        try
        {
            // Извлечение userId из токена
            var userId = GetUserIdFromToken();
            if (userId == null)
            {
                return Unauthorized(new { error = "Invalid token" });
            }

            var request = new PurchaseRequest
            {
                UserId = userId,
                ItemId = requestData.ItemId,
                PaymentMethod = requestData.PaymentMethod
            };

            var result = await _purchaseProcessor.ProcessPurchaseAsync(request);

            if (!result.Success)
            {
                return BadRequest(new { error = result.Error });
            }

            // Успешный ответ
            return Ok(new 
            { 
                success = true, 
                transactionId = result.TransactionId,
                message = "Покупка успешно завершена"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing purchase");
            return StatusCode(500, new { error = "Internal server error" });
        }
    }

    [HttpGet("products")]
    public async Task<IActionResult> GetProducts()
    {
        try
        {
            var products = await _productCatalog.GetAvailableItemsAsync();
            
            var response = products.Select(p => new ProductResponse
            {
                Id = p.Id,
                Name = p.Name,
                Price = p.Price,
                Category = p.Category,
                RequiredLevel = p.RequiredLevel
            });
            
            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting products");
            return StatusCode(500, new { error = "Internal server error" });
        }
    }

    // DRY: Вынесенный метод для получения userId из токена
    private string? GetUserIdFromToken()
    {
        return User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
    }
}

public class PurchaseRequest
{
    [Required]
    public string ItemId { get; set; } = string.Empty;
    
    [Required]
    public string PaymentMethod { get; set; } = string.Empty;
}

public class ProductResponse
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public decimal Price { get; set; }
    public string Category { get; set; } = string.Empty;
    public int RequiredLevel { get; set; }
}
