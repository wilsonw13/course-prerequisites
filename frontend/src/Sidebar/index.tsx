import { useState, useEffect, Dispatch, SetStateAction, ChangeEvent, FormEvent } from 'react'
import { RxDoubleArrowLeft } from 'react-icons/rx'
import styles from './Sidebar.module.css'
import { Query, QueryValue, QueryOption } from '../interfaces'

interface Props {
  query: Query | null,
  setQuery: Dispatch<SetStateAction<Query | null>>,
  queryOptions: QueryOption[],
  sendQuery: (s: WebSocket | null | undefined, q: Query | null) => void
}

export interface QueryValid {
  [key: string]: boolean;
}

export default function Sidebar ({ query, queryOptions, setQuery, sendQuery }: Props) {
  const [isOpen, setOpen] = useState<boolean>(true)
  const [isQueryValid, setQueryValid] = useState<QueryValid>({})

  const allQueriesValid = () => Object.values(isQueryValid).every(Boolean)

  // TODO: Memoize query options
  // Update whenever query options changes
  useEffect(() => {
    // updates the query object when the query options change
    const newQuery: Query = queryOptions.reduce((acc: Query, option: QueryOption) => {
      acc[option.id] = option.default_value
      return acc
    }, {})

    setQuery(newQuery)

    // sends the default query to the server when the query options change
    sendQuery(undefined, newQuery)

    // updates the query validation object when the query options change
    const newQueryValid: QueryValid = queryOptions.reduce((acc: QueryValid, option: QueryOption) => {
      if (option.input_validation) acc[option.id] = true
      return acc
    }, {})

    setQueryValid(newQueryValid)
  }, [queryOptions])

  const containerStyle = `${styles.sidebar} ${isOpen ? '' : styles.sidebar_collapsed}`
  const arrowIronStyle = `${styles.arrow_icon} ${isOpen ? '' : styles.rotate_arrow_icon}`

  // Update whenever input form changes (i.e. when the query changes)
  const handleInputChange = (e: ChangeEvent<HTMLFormElement>) => {
    const { name, value, type, checked } = e.target
    let inputValue: QueryValue

    console.log('Input Change:', name, value, type, checked)

    switch (type) {
      case 'text': {
        // Remove multiple whitespaces
        inputValue = value.replace(/\s{2}/g, ' ')

        // Gets the correct regex from the query options
        const regex = new RegExp(queryOptions.find((option) => option.id === name)?.input_validation as string)

        // Updates the query validation object
        setQueryValid((prevState) => ({
          ...prevState,
          [name]: regex.test(inputValue as string)
        }))

        break
      }
      case 'checkbox':
        inputValue = checked

        break

      case 'number':

        break // TODO
    }

    // Updates the query object
    setQuery((prevState) => ({
      ...prevState,
      [name]: inputValue
    }))
  }

  // Submit handler for the input form
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    sendQuery()
  }

  // Renders the correct type of input field based on the query option (e.g. text, number, checkbox)
  const renderInput = ({ id, value_type, input_placeholder }: QueryOption) => {
    const value = query?.[id] as string | number | boolean

    switch (value_type) {
      case 'string':
        return (
        <input
          type="text"
          name={id}
          placeholder={input_placeholder}
          value={value as string}
          className={isQueryValid[id] ? '' : styles.invalid}
        />
        )
      case 'number':
        return (
        <input
          type="number"
          name={id}
          placeholder={input_placeholder}
          value={value as number}
          className={isQueryValid[id] ? '' : styles.invalid}
        />
        )
      case 'boolean':
        return (
        <input
          type="checkbox"
          name={id}
          checked={value as boolean}
        />
        )
      default:
        return null
    }
  }

  // Creates the input fields (container + label + input) for the query options
  const formFields = queryOptions.map((option) => (
    <div key={option.id}>
      <label htmlFor={option.id}>{option.display_name}</label>
      {renderInput(option)}
    </div>
  ))

  return (
    <div className={containerStyle}>
      <RxDoubleArrowLeft className={arrowIronStyle} onClick={() => { setOpen(!isOpen) }} />
      <form className={styles.form} onChange={handleInputChange} onSubmit={handleSubmit}>
        <h1>Query Courses</h1>
        {formFields}
        <button
          className={allQueriesValid() ? '' : styles.submitDisabled}
          disabled={!allQueriesValid()}>Query</button>
      </form>
    </div>
  )
}
