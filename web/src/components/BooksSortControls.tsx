import { 
  Box, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  IconButton, 
  Tooltip,
  SelectChangeEvent,
} from '@mui/material'
import { ArrowUpward, ArrowDownward } from '@mui/icons-material'
import { SortField, SortOptions, SORT_FIELD_LABELS } from '../types/sorting'

interface BooksSortControlsProps {
  sortOptions: SortOptions
  onSortChange: (sortOptions: SortOptions) => void
}

const BooksSortControls = ({ sortOptions, onSortChange }: BooksSortControlsProps) => {
  const handleFieldChange = (event: SelectChangeEvent<SortField>) => {
    onSortChange({
      ...sortOptions,
      field: event.target.value as SortField,
    })
  }

  const handleOrderToggle = () => {
    onSortChange({
      ...sortOptions,
      order: sortOptions.order === 'asc' ? 'desc' : 'asc',
    })
  }

  const getSortIcon = () => {
    if (sortOptions.order === 'asc') {
      return <ArrowUpward />
    } else {
      return <ArrowDownward />
    }
  }

  return (
    <Box display="flex" alignItems="center" gap={1}>
      <FormControl size="small" sx={{ minWidth: 160 }}>
        <InputLabel id="sort-field-label">Sort by</InputLabel>
        <Select
          labelId="sort-field-label"
          value={sortOptions.field}
          label="Sort by"
          onChange={handleFieldChange}
        >
          {Object.entries(SORT_FIELD_LABELS).map(([field, label]) => (
            <MenuItem key={field} value={field}>
              {label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      
      <Tooltip title={`Sort ${sortOptions.order === 'asc' ? 'ascending' : 'descending'}`}>
        <IconButton 
          onClick={handleOrderToggle}
          size="small"
          sx={{ 
            border: 1, 
            borderColor: 'divider',
            '&:hover': {
              backgroundColor: 'action.hover'
            }
          }}
        >
          {getSortIcon()}
        </IconButton>
      </Tooltip>
    </Box>
  )
}

export default BooksSortControls