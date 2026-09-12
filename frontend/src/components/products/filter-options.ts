import type { ProductSort } from '@/api/products'

export const REGIONS = [
  { value: '', label: 'All regions' },
  { value: 'JO', label: 'Jordan' },
  { value: 'SA', label: 'Saudi Arabia' },
]

export const SORT_OPTIONS: Array<{ value: ProductSort; label: string }> = [
  { value: 'default', label: 'Featured' },
  { value: 'price_asc', label: 'Price: low to high' },
  { value: 'price_desc', label: 'Price: high to low' },
]
