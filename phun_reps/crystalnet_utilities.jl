
# This returns the coordinates of the subnets to match the .vtf format that can be automatically exported from CrystaNets
# This is what used for PHuN. This might not be the most efficient way but was done so I could verify against the .vtf files exported from CrystalNets
function _vtf_ordered_coords(net; repeatedges=2)
    net3 = CrystalNets.CrystalNet3D(net)
    pge = net3.pge
    n = PeriodicGraphs.nv(pge.g)

    invcorres = [PeriodicGraphs.PeriodicVertex3D(i) for i in 1:n]
    corres = Dict{PeriodicGraphs.PeriodicVertex3D,Int}(invcorres[i] => i for i in 1:n)

    j = n + 1
    for _ in 1:repeatedges
        jmax = j - 1
        for i in 1:jmax
            vertex = invcorres[i]
            for y in PeriodicGraphs.neighbors(pge.g, vertex)
                if get!(corres, y, j) == j
                    j += 1
                    push!(invcorres, y)
                end
            end
        end
    end

    mat = Float64.(pge.cell.mat)
    coords = Matrix{Float64}(undef, length(invcorres), 3)

    for (i, x) in enumerate(invcorres)
        pos = Float64.(collect(pge.pos[x.v]))
        ofs = Float64.(collect(x.ofs))
        coords[i, :] = mat * (pos .+ ofs)
    end

    return coords, mat
end

# This gets the coordinates and cell matrices for all CrystalNet objects in the UnderlyingNets structure
# It returns a list of coordinate matrices and a list of cell matrices
function get_net_coords(path, options)
    group = CrystalNets.UnderlyingNets(CrystalNets.parse_chemfile(path, options))

    coords_list = Matrix{Float64}[]
    mat_list = Matrix{Float64}[]

    for subgroups in (group.D1, group.D2, group.D3)
        isempty(subgroups) && continue

        for (nets, _nfold, _id) in subgroups
            isempty(nets) && continue

            for net in nets
                net isa CrystalNets.CrystalNet || continue
                coords, mat = _vtf_ordered_coords(net; repeatedges=2)
                push!(coords_list, coords)
                push!(mat_list, mat)
            end
        end
    end

    isempty(coords_list) && error("No CrystalNet objects found in UnderlyingNets")

    return coords_list, mat_list
end

