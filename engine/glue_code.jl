import JSON

timed_function_call(f, input) = @timed f(input...)

function json_array_dim(a)
    if length(size(a)) > 0
        return 1 + json_array_dim(a[1])
    else
        return 0
    end
end

function json_array_eltype(a)
    if eltype(a) == Any
        return json_array_eltype(a[1])
    else
        return eltype(a)
    end
end

juliafy_json(t) = t
juliafy_json(a::Array) = convert(Array{{json_array_eltype(a), json_array_dim(a)}}, hcat(a...))

tupleit(t) = tuple(t)
tupleit(t::Tuple) = t

input_tuples = JSON.Parser.parsefile("{:s}")

for (i, input_tuple) in enumerate(input_tuples)

    input_tuple = [juliafy_json(elem) for elem in input_tuple]

    output_tuple = $FUNCTION_NAME(input_tuple...) |> tupleit

    open("{:s}.output$i.json", "w") do f
       JSON.print(f, output_tuple)
    end
end
