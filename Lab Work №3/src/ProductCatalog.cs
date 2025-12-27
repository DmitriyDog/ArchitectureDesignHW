// SOLID: Interface Segregation
public interface IProductCatalog
{
    Task<Product?> GetItemAsync(string itemId);
    Task<IEnumerable<Product>> GetAvailableItemsAsync();
}

public class ProductCatalog : IProductCatalog
{
    private readonly IProductRepository _repository;
    private readonly ILogger<ProductCatalog> _logger;

    public ProductCatalog(
        IProductRepository repository,
        ILogger<ProductCatalog> logger)
    {
        _repository = repository;
        _logger = logger;
    }

    // KISS: Простой метод получения товара
    public async Task<Product?> GetItemAsync(string itemId)
    {
        try
        {
            var product = await _repository.GetItemAsync(itemId);
            
            if (product == null)
            {
                _logger.LogWarning("Product not found: {ItemId}", itemId);
                return null;
            }

            // YAGNI: Не добавляем кэширование, пока нет реальной нагрузки
            return product;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting product: {ItemId}", itemId);
            throw;
        }
    }

    public async Task<IEnumerable<Product>> GetAvailableItemsAsync()
    {
        return await _repository.GetAvailableItemsAsync();
    }
}

// SOLID: Dependency Inversion - абстракция репозитория
public interface IProductRepository
{
    Task<Product?> GetItemAsync(string itemId);
    Task<IEnumerable<Product>> GetAvailableItemsAsync();
}

public class ProductRepository : IProductRepository
{
    private readonly ApplicationDbContext _context;

    public ProductRepository(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<Product?> GetItemAsync(string itemId)
    {
        // DRY: Используем стандартный подход к запросам
        return await _context.Products
            .AsNoTracking()
            .FirstOrDefaultAsync(p => p.Id == itemId && p.IsAvailable);
    }

    public async Task<IEnumerable<Product>> GetAvailableItemsAsync()
    {
        return await _context.Products
            .AsNoTracking()
            .Where(p => p.IsAvailable)
            .OrderBy(p => p.Category)
            .ThenBy(p => p.Name)
            .ToListAsync();
    }
}

// KISS: Простая модель товара
public class Product
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public decimal Price { get; set; }
    public string Category { get; set; } = string.Empty;
    public bool IsAvailable { get; set; }
    public int RequiredLevel { get; set; } = 1;
    
    // YAGNI: Только необходимые методы
    public bool CanBePurchasedBy(int playerLevel) 
        => IsAvailable && playerLevel >= RequiredLevel;
}
