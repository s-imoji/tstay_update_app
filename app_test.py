from app import get_yesterday_string, query_string

if __name__ == '__main__':
    yesterday_string_val = get_yesterday_string()
    query_string_val = query_string()
    
    print(yesterday_string_val)
    print(query_string_val)
