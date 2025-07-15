# Order Book Implementation

A Python implementation of a financial order book with price-time priority matching.

## Features

- **Price-Time Priority**: Orders matched by best price first, then by arrival time
- **Partial Fills**: Orders can be partially matched and remain in the book
- **Order Management**: Add, cancel, and query order status
- **Multi-Symbol Support**: Handle multiple trading instruments simultaneously
- **Efficient Data Structures**: Uses `SortedDict` for price levels and `deque` for time priority

## Order Matching Logic

1. **Buy orders** match against sell orders at or below the buy price
2. **Sell orders** match against buy orders at or above the sell price
3. **Remaining quantity** stays in the order book if not fully matched
4. **Cancelled orders** are skipped during matching but remain in memory

## Dependencies

- `sortedcontainers` - For efficient price-level management
- `collections` - For deque and defaultdict
