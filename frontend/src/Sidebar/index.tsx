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

  const handleInputChange = (e: ChangeEvent<HTMLFormElement>) => {
    const { name, value, type, checked } = e.target
    let inputValue: QueryValue

    console.log('Input Change:', name, value, type, checked)

    switch (type) {
      case 'text': {
        // Remove multiple whitespaces
        inputValue = value.replace(/\s{2}/g, ' ')

        // Validate input values
        const regex = new RegExp(queryOptions.find((option) => option.id === name)?.input_validation as string)

        console.log(regex, regex.test(inputValue as string))

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

    setQuery((prevState) => ({
      ...prevState,
      [name]: inputValue
    }))

    // if (type === 'checkbox') {
    //   inputValue = checked
    // } else if (name === 'courses' || name === 'departments') {
    //   // Remove all whitespace and convert to uppercase and trim
    //   inputValue = value.toUpperCase().replace(/\s{2}/g, ' ')

    //   // Validate input values
    //   let regex: RegExp
    //   switch (name) {
    //     case 'courses':
    //       regex = /^[A-Z]{3}\s?\d{3}\s*(?:,\s*[A-Z]{3}\s?\d{3})*$/
    //       break
    //     case 'departments':
    //       regex = /^[A-Z]{3}\s*(?:,\s*[A-Z]{3})$/
    //       break
    //   }

    //   setQueryValid((prevState) => ({
    //     ...prevState,
    //     [name]: regex.test(`${inputValue}`)
    //   }))
    // } else {
    //   inputValue = value
    // }

    setQuery((prevState) => ({
      ...prevState,
      [name]: inputValue
    }))
  }

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    sendQuery()
  }

  const containerStyle = `${styles.sidebar} ${isOpen ? '' : styles.sidebar_collapsed}`
  const arrowIronStyle = `${styles.arrow_icon} ${isOpen ? '' : styles.rotate_arrow_icon}`

  const renderInput = ({ id, display_name, value_type, input_placeholder, input_validation, character_limit }: QueryOption) => {
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
        {/* <div>
          <label htmlFor="courses">Courses</label>
          <input
            type="text"
            name="courses"
            value={query.courses}
          />
        </div>
        {!isQueryValidObj.courses && <p style={{ color: 'red' }}>Please enter valid courses!</p>}
        <div>
          <label htmlFor="departments">Departments</label>
          <input
            type="text"
            name="departments"
            value={query.departments}
          />
        </div>
        {!isQueryValidObj.departments && <p style={{ color: 'red' }}>Please enter valid departments!</p>}

        <div>
          <label htmlFor="show_transitive_prereqs">
            Show Transitive Prerequisites
          </label>
          <input
            type="checkbox"
            name="show_transitive_prereqs"
            checked={query.show_transitive_prereqs}
          />
        </div>

        <div>
          <label htmlFor="remove_courses_without_prereqs">
            Show Disconnected Courses
          </label>
          <input
            type="checkbox"
            name="remove_courses_without_prereqs"
            checked={query.remove_courses_without_prereqs}
          />
        </div> */}
        <button
          className={allQueriesValid() ? '' : styles.submitDisabled}
          disabled={!allQueriesValid()}>Query</button>
      </form>
    </div>
  )
}
