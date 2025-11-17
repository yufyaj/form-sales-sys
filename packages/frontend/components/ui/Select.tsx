import * as React from 'react'
import { cn } from '@/lib/utils'

export interface SelectOption {
  value: string | number
  label: string
}

export interface SelectProps
  extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'value'> {
  label?: string
  error?: string
  options: SelectOption[]
  placeholder?: string
  value?: string | number
}

/**
 * モダンなセレクトコンポーネント
 *
 * @example
 * ```tsx
 * <Select
 *   label="顧客企業"
 *   options={[
 *     { value: 1, label: '株式会社A' },
 *     { value: 2, label: '株式会社B' }
 *   ]}
 *   placeholder="顧客企業を選択してください"
 * />
 * ```
 */
const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, options, placeholder, id, value, ...props }, ref) => {
    const selectId = id || label?.toLowerCase().replace(/\s+/g, '-')

    return (
      <div className="w-full space-y-2">
        {label && (
          <label
            htmlFor={selectId}
            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            {label}
          </label>
        )}
        <select
          id={selectId}
          value={value}
          className={cn(
            'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
            'disabled:cursor-not-allowed disabled:opacity-50',
            'transition-all duration-base',
            error && 'border-destructive focus-visible:ring-destructive',
            className
          )}
          ref={ref}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? `${selectId}-error` : undefined}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {error && (
          <p
            id={`${selectId}-error`}
            className="text-sm font-medium text-destructive animate-in slide-in-from-top-1"
            role="alert"
          >
            {error}
          </p>
        )}
      </div>
    )
  }
)

Select.displayName = 'Select'

export default Select
export { Select }
