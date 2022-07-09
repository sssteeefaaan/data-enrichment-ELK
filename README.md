<body>
    <h1>
        Data enrichment using ELK stack
    </h1>
    <h2>
        Tutorial
    </h2>
    In console run
    <pre>docker-compose -p data_enrichment up --build</pre>
    <h2>Containers</h2>
    <ul>
        <li>
            HTTP input for logstash is on <a href="http://localhost:9998">http://localhost:9998</a>
        </li>
        <li>
            Flask server is on <a href="http://localhost:9999">http://localhost:9999</a> with currently available endpoints:
            <ul>
                <li>
                    <pre>GET /enrich</pre>
                </li>
            </ul>
        </li>
    </ul>
</body>
