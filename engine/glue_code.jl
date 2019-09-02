import JSON

timed_function_call(f, input) = @timed f(input...)

function json_arr_dim(a)
    if length(size(a)) > 0
        return 1 + json_arr_dim(a[1])
    else
        return 0
    end
end

function json_arr_eltype(a)
    if eltype(a) == Any
        return json_arr_eltype(a[1])
    else
        return eltype(a)
    end
end

juliafy_json(a::Array) = convert(Array{{json_arr_eltype(a), json_arr_dim(a)}}, hcat(a...))
juliafy_json(t) = t

input_tuples = JSON.Parser.parsefile("{:s}")

for (i, it) in enumerate(input_tuples)
    it = [juliafy_json(elem) for elem in it]
    ot = $FUNCTION_NAME(it...)
    open("{:s}.output$i.pickle", "w") do f
       JSON.print(f, ot)
    end
end